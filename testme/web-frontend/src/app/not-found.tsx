import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4">404</h1>
        <h2 className="text-2xl font-semibold mb-4">페이지를 찾을 수 없습니다</h2>
        <p className="text-gray-600 mb-8">
          요청하신 페이지가 존재하지 않습니다.
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-emerald-600 text-white rounded-md hover:bg-emerald-700"
        >
          홈으로 돌아가기
        </Link>
      </div>
    </div>
  );
}

