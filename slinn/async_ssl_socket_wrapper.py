import ssl
import asyncio


class AsyncSSLSocketWrapper:
    def __init__(self, sock, ssl_context, loop):
        self._sock = sock
        self.loop = loop
        self._sock.setblocking(False)

        self._in_bio = ssl.MemoryBIO()
        self._out_bio = ssl.MemoryBIO()
        self._ssl_obj = ssl_context.wrap_bio(
            self._in_bio,
            self._out_bio,
            server_side=True
        )
        self._handshake_complete = False

    async def do_handshake(self):
        """Асинхронное выполнение SSL-рукопожатия"""
        while not self._handshake_complete:
            # Сначала попытаемся выполнить рукопожатие
            try:
                self._ssl_obj.do_handshake()
                self._handshake_complete = True
                await self._flush_out_bio()
                return
            except ssl.SSLWantReadError:
                # Нужно больше данных - прочитать из сокета
                await self._process_handshake_read()
            except ssl.SSLWantWriteError:
                # Нужно отправить данные - записать в сокет
                await self._process_handshake_write()

    async def _process_handshake_read(self):
        """Обработка ситуации, когда SSL требует больше данных"""
        # Сначала сбросим исходящие данные (если есть)
        if self._out_bio.pending:
            await self._flush_out_bio()

        # Затем прочитаем входящие данные
        await self._feed_in_bio()

    async def _process_handshake_write(self):
        """Обработка ситуации, когда SSL требует отправки данных"""
        # Сначала сбросим исходящие данные
        await self._flush_out_bio()

        # Затем проверим, не появились ли входящие данные
        # (некоторые реализации SSL могут требовать чтения после записи)
        if self._sock in select.select([self._sock], [], [], 0)[0]:
            await self._feed_in_bio()

    async def _feed_in_bio(self):
        """Чтение данных из сокета во входной BIO"""
        try:
            # Читаем до 16K за раз (максимальный размер TLS-записи)
            data = await self.loop.sock_recv(self._sock, 16384)
            if not data:
                raise ConnectionResetError("Соединение закрыто клиентом")
            self._in_bio.write(data)
        except BlockingIOError:
            # В асинхронном режиме не должно происходить
            pass
        except OSError as e:
            if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                raise

    async def _flush_out_bio(self):
        """Запись данных из выходного BIO в сокет"""
        while self._out_bio.pending:
            data = self._out_bio.read()
            if data:
                await self.loop.sock_sendall(self._sock, data)

    async def recv(self, n_bytes):
        """Асинхронное чтение данных"""
        if not self._handshake_complete:
            await self.do_handshake()

        while True:
            try:
                data = self._ssl_obj.read(n_bytes)
                if not data:
                    # EOF от SSL слоя
                    return b''
                return data
            except ssl.SSLWantReadError:
                await self._process_handshake_read()
            except ssl.SSLWantWriteError:
                await self._process_handshake_write()
            except ssl.SSLZeroReturnError:
                # Корректное закрытие соединения
                return b''

    async def send(self, data):
        """Асинхронная отправка данных"""
        if not self._handshake_complete:
            await self.do_handshake()

        total_sent = 0
        while total_sent < len(data):
            try:
                sent = self._ssl_obj.write(data[total_sent:])
                total_sent += sent
                await self._flush_out_bio()
            except ssl.SSLWantReadError:
                await self._process_handshake_read()
            except ssl.SSLWantWriteError:
                await self._process_handshake_write()

    # Остальные методы остаются без изменений
    def settimeout(self, timeout):
        self._sock.settimeout(timeout)

    def setblocking(self, blocking):
        self._sock.setblocking(blocking)

    def getsockopt(self, *args):
        return self._sock.getsockopt(*args)

    def fileno(self):
        return self._sock.fileno()

    def close(self):
        try:
            # Попытка корректного завершения SSL-сессии
            if self._handshake_complete:
                self._ssl_obj.unwrap()
                self._flush_out_bio()
        finally:
            self._sock.close()