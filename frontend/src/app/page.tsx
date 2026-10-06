import MemoryBridge from "@/components/MemoryBridge";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 dark:bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <MemoryBridge />
      </div>
    </main>
  );
}
