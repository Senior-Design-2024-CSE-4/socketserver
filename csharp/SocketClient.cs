using System.Net;
using System.Net.Sockets;
using System.Text;

namespace Client
{
    public class SocketClient
    {
        int port;
        string host;
        private TcpClient? tcpSocket;
        private UdpClient? udpSocket;

        public SocketClient()
        {
            port = -1;
            host = "";
        }

        public void Connect(int port, string host)
        {
            this.port = port;
            this.host = host;
            Console.WriteLine("Connecting to host " + host + "at port " + port.ToString());
            try
            {
                tcpSocket = new TcpClient(host, port);
                Console.WriteLine("TCP Connection successful.");

                // udpSocket = new UdpClient(host, port);
                // Console.WriteLine("UDP Connection successful.");
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }
    }
}

