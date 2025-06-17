import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
            MindMirror
          </h1>
        <p className="text-lg text-gray-600 mb-8">
          User app coming soon...
        </p>
        <Link 
          href="/landing"
          className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-gray-900 border border-transparent rounded-lg shadow-sm hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 transition-colors"
              >
          View Landing Page
        </Link>
        </div>
    </div>
  );
}