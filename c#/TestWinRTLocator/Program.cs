using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using Windows.Devices.Geolocation;

namespace TestWinRTLocator
{
    [StructLayout(LayoutKind.Sequential)]
    public class PowerState
    {
        public ACLineStatus ACLineStatus;
        public BatteryFlag BatteryFlag;
        public Byte BatteryLifePercent;
        public Byte Reserved1;
        public Int32 BatteryLifeTime;
        public Int32 BatteryFullLifeTime;

        // direct instantation not intended, use GetPowerState.
        private PowerState() { }

        public static PowerState GetPowerState()
        {
            PowerState state = new PowerState();
            if (GetSystemPowerStatusRef(state))
                return state;

            throw new ApplicationException("Unable to get power state");
        }

        [DllImport("Kernel32", EntryPoint = "GetSystemPowerStatus")]
        private static extern bool GetSystemPowerStatusRef(PowerState sps);
    }

    // Note: Underlying type of byte to match Win32 header
    public enum ACLineStatus : byte
    {
        Offline = 0, Online = 1, Unknown = 255
    }

    public enum BatteryFlag : byte
    {
        High = 1, Low = 2, Critical = 4, Charging = 8,
        NoSystemBattery = 128, Unknown = 255
    }
    
    class Program
    {
        static int pointsCount = 0;
        static Geolocator locator;
        static DateTimeOffset lastPointTime = DateTimeOffset.Now;
        static DateTimeOffset lastAsyncPointTime;
        static void Main(string[] args)
        {
            locator = new Geolocator();
            locator.ReportInterval = 2000;
            locator.DesiredAccuracy = PositionAccuracy.High;
            locator.PositionChanged += locator_PositionChanged;
            locator.StatusChanged += locator_StatusChanged;
            locator.MovementThreshold = 2;

            Microsoft.Win32.SystemEvents.PowerModeChanged += SystemEvents_PowerModeChanged;
            int counter = 0;
            while (pointsCount <= 20)
            {
                System.Threading.Thread.Sleep(1000);
                PowerState pow = PowerState.GetPowerState();
                Console.WriteLine(DateTimeOffset.Now.ToLocalTime() + " tik " + pow.ACLineStatus + ", bat:" + pow.BatteryLifePercent+"%, "+pow.BatteryFlag);
                if (++counter > 10)
                {
                    showLocation();
                    counter = 0;
                }
            }
        }

        static void SystemEvents_PowerModeChanged(object sender, Microsoft.Win32.PowerModeChangedEventArgs e)
        {
            Console.WriteLine(DateTimeOffset.Now.ToLocalTime() + "\tPower mode change to " + e.Mode + " ");
        }

        async static void showLocation()
        {
            Geoposition pos = await locator.GetGeopositionAsync();
            if (pos.Coordinate.Timestamp == lastAsyncPointTime)
            {
                Console.WriteLine("async-get returns previous timestamp.");
            }
            else
            {
                Console.WriteLine("async get location result = " + geoPosToStr(pos) + "\npoint time diff =" + (pos.Coordinate.Timestamp - lastAsyncPointTime));
            }
            lastAsyncPointTime = pos.Coordinate.Timestamp;
        }

        static void locator_StatusChanged(Geolocator sender, StatusChangedEventArgs args)
        {
            
            Console.WriteLine(DateTimeOffset.Now.ToLocalTime() + "\tlocator status=\t" + args.Status);
        }

        static void locator_PositionChanged(Geolocator sender, PositionChangedEventArgs args)
        {
            Console.WriteLine(DateTimeOffset.Now.ToLocalTime() + "\tposition #" + pointsCount + ":\t" + geoPosToStr(args.Position));
            Console.WriteLine("\t\ttime left from last point:" + (DateTimeOffset.Now - lastPointTime));
            pointsCount++;
            lastPointTime = DateTimeOffset.Now;
        }
        static string geoPosToStr(Geoposition pos)
        {
            return "t=" + pos.Coordinate.Timestamp.ToLocalTime() + " " + pos.Coordinate.Latitude + "x" + pos.Coordinate.Longitude
                + "\tspeed=" + pos.Coordinate.Speed
                + "\taccuracy=" + pos.Coordinate.Accuracy;
        }
    }
}
