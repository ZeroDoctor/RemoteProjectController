using System;
using System.Collections;
using System.Diagnostics;

namespace OpenWindow
{

    class Program
    {
        public Program(ArrayList closeprograms, bool keep_open)
        {
            Process[] processlist = Process.GetProcesses();

            foreach (Process process in processlist)
            {
                if (!String.IsNullOrEmpty(process.MainWindowTitle))
                {
                    Console.WriteLine("Process: {0} ID: {1} Window title: {2}", process.ProcessName, process.Id, process.MainWindowTitle);
                    if(!keep_open && closeprograms.Contains(process.ProcessName + ".exe"))
                        process.Kill();
                }
            }
        }

        static void Main(string[] args)
        {
            ArrayList closeprograms = new ArrayList();
            bool keep_open = false;

            if (args[0].Contains("--peek"))
            {
                keep_open = true;
            }
            else
            {
                for (int i = 0; i < args.Length; i++)
                {
                    Console.WriteLine(args[i]);
                    closeprograms.Add(args[i]);
                }
            }

            if (closeprograms.Count > 0 || keep_open)
            {
                new Program(closeprograms, keep_open);
            }
        }
    }
}
