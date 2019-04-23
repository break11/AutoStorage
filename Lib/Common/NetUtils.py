
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

socketErrorString = {
    0  : "QAbstractSocket::ConnectionRefusedError	         The connection was refused by the peer (or timed out).",
    1  : "QAbstractSocket::RemoteHostClosedError	         The remote host closed the connection. Note that the client socket (i.e., this socket) will be closed after the remote close notification has been sent.",
    2  : "QAbstractSocket::HostNotFoundError	             The host address was not found.",
    3  : "QAbstractSocket::SocketAccessError	             The socket operation failed because the application lacked the required privileges.",
    4  : "QAbstractSocket::SocketResourceError	             The local system ran out of resources (e.g., too many sockets).",
    5  : "QAbstractSocket::SocketTimeoutError	             The socket operation timed out.",
    6  : "QAbstractSocket::DatagramTooLargeError	         The datagram was larger than the operating system's limit (which can be as low as 8192 bytes).",
    7  : "QAbstractSocket::NetworkError	                     An error occurred with the network (e.g., the network cable was accidentally plugged out).",
    8  : "QAbstractSocket::AddressInUseError	             The address specified to QAbstractSocket::bind() is already in use and was set to be exclusive.",
    9  : "QAbstractSocket::SocketAddressNotAvailableError	 The address specified to QAbstractSocket::bind() does not belong to the host.",
    10 : "QAbstractSocket::UnsupportedSocketOperationError   The requested socket operation is not supported by the local operating system (e.g., lack of IPv6 support).",
    12 : "QAbstractSocket::ProxyAuthenticationRequiredError  The socket is using a proxy, and the proxy requires authentication.",
    13 : "QAbstractSocket::SslHandshakeFailedError		     The SSL/TLS handshake failed, so the connection was closed (only used in QSslSocket)",
    11 : "QAbstractSocket::UnfinishedSocketOperationError	 Used by QAbstractSocketEngine only, The last operation attempted has not finished yet (still in progress in the background).",
    14 : "QAbstractSocket::ProxyConnectionRefusedError		 Could not contact the proxy server because the connection to that server was denied",
    15 : "QAbstractSocket::ProxyConnectionClosedError		 The connection to the proxy server was closed unexpectedly (before the connection to the final peer was established)",
    16 : "QAbstractSocket::ProxyConnectionTimeoutError		 The connection to the proxy server timed out or the proxy server stopped responding in the authentication phase.",
    17 : "QAbstractSocket::ProxyNotFoundError		         The proxy address set with setProxy() (or the application proxy) was not found.",
    18 : "QAbstractSocket::ProxyProtocolError		         The connection negotiation with the proxy server failed, because the response from the proxy server could not be understood.",
    19 : "QAbstractSocket::OperationError		             An operation was attempted while the socket was in a state that did not permit it.",
    20 : "QAbstractSocket::SslInternalError		             The SSL library being used reported an internal error. This is probably the result of a bad installation or misconfiguration of the library.",
    21 : "QAbstractSocket::SslInvalidUserDataError		     Invalid data (certificate, key, cypher, etc.) was provided and its use resulted in an error in the SSL library.",
    22 : "QAbstractSocket::TemporaryError		             A temporary error occurred (e.g., operation would block and socket is non-blocking).",
    -1 : "QAbstractSocket::UnknownSocketError		         An unidentified error occurred.",
    }

def socketErrorToString( errorCode ):
    return socketErrorString[ errorCode ]
