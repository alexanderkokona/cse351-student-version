using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Threading;

namespace assignment11
{
    public class Program
    {
        private const long START_NUMBER = 10_000_000_000;
        private const int RANGE_COUNT = 1_000_000;
        private const int WORKER_COUNT = 10;

        static void Main(string[] args)
        {
            // Thread-safe queue
            var queue = new ConcurrentQueue<long>();

            // Used to block workers when queue is empty
            var itemAvailable = new SemaphoreSlim(0);

            // Worker threads
            Thread[] workers = new Thread[WORKER_COUNT];

            int primesFound = 0;
            object consoleLock = new object();

            // Worker thread method
            void Worker()
            {
                while (true)
                {
                    itemAvailable.Wait();

                    if (!queue.TryDequeue(out long number))
                        continue;

                    // Sentinel: stop signal
                    if (number == -1)
                        return;

                    if (IsPrime(number))
                    {
                        Interlocked.Increment(ref primesFound);

                        lock (consoleLock)
                        {
                            Console.Write($"{number}, ");
                        }
                    }
                }
            }

            var stopwatch = Stopwatch.StartNew();

            // Start workers
            for (int i = 0; i < WORKER_COUNT; i++)
            {
                workers[i] = new Thread(Worker);
                workers[i].Start();
            }

            // Main thread enqueue numbers
            for (long n = START_NUMBER; n < START_NUMBER + RANGE_COUNT; n++)
            {
                queue.Enqueue(n);
                itemAvailable.Release();
            }

            // Send sentinel values (one for each worker)
            for (int i = 0; i < WORKER_COUNT; i++)
            {
                queue.Enqueue(-1);
                itemAvailable.Release();
            }

            // Wait for all workers to finish
            foreach (var worker in workers)
                worker.Join();

            stopwatch.Stop();

            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine($"Primes found      = {primesFound}");
            Console.WriteLine($"Total time        = {stopwatch.Elapsed}");
        }

        // Efficient prime test
        private static bool IsPrime(long n)
        {
            if (n <= 3) return n > 1;
            if (n % 2 == 0 || n % 3 == 0) return false;

            for (long i = 5; i * i <= n; i += 6)
            {
                if (n % i == 0 || n % (i + 2) == 0)
                    return false;
            }
            return true;
        }
    }
}
