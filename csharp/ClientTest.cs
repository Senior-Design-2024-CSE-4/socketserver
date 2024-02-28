using Client;

namespace Main
{
    public class ClientTest
    {
        public static void Main(string[] args)
        {
            SocketClient client = new();
            client.Connect(12345, "localhost");
        }
    }
}
