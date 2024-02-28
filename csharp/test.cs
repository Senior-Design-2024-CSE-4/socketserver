// void Main()
// {
// 	SocketClient.StartClient(); 
// }

// public class SocketClient
// {
//     public static int Main(String[] args)
//     {
//         StartClient();
//         return 0;
//     }
	
// 	public static void SendData(Socket sender) 
// 	{
// 		for (int i = 0; i < 1000; i++)
// 		{
// 			string data = "test packet {i}";
// 			int bytes = sender.Send(Encoding.ASCII.GetBytes(data));
// 		}
// 	}

//     public static void StartClient()
//     {
//         byte[] bytes = new byte[1024];
// 		try
//         {
//             IPHostEntry host = Dns.GetHostEntry("localhost");
//             IPAddress ipAddress = host.AddressList[1];
// 			Console.Write(ipAddress);
//             IPEndPoint remoteEP = new IPEndPoint(ipAddress, 12345);

//             Socket sender = new Socket(ipAddress.AddressFamily,
//                 SocketType.Stream, ProtocolType.Tcp);

//             try
//             {
//                 sender.Connect(remoteEP);

//                 Console.WriteLine("Socket connected to {0}",
//                     sender.RemoteEndPoint.ToString());

//                 byte[] msg = Encoding.ASCII.GetBytes("r:csharp");

//                 int bytesSent = sender.Send(msg);

//                 int bytesRec = sender.Receive(bytes);
//                 Console.WriteLine("Availible Clients {0}",
//                     Encoding.ASCII.GetString(bytes, 0, bytesRec));
// 				Console.WriteLine("Pick a Client");
// 				string destination = Console.ReadLine();
// 				int bytesSent2 = sender.Send(Encoding.ASCII.GetBytes(destination));
// 				Console.WriteLine("Ready to Send");
// 				string useless = Console.ReadLine();

// 				SendData(sender);

//                 sender.Shutdown(SocketShutdown.Both);
//                 sender.Close();

//             }
            
//             catch (Exception e)
//             {
//                 Console.WriteLine("Unexpected exception : {0}", e.ToString());
//             }

//         }
//         catch (Exception e)
//         {
//             Console.WriteLine(e.ToString());
//         }
//     }
// }