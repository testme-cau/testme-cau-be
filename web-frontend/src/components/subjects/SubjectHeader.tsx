import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Subject } from "@/types/api";
import { ArrowLeft, ClipboardList } from "lucide-react";

interface SubjectHeaderProps {
  subject: Subject;
  subjectId: string;
}

export function SubjectHeader({ subject, subjectId }: SubjectHeaderProps) {
  return (
    <div>
      <Link href="/dashboard">
        <Button variant="ghost" className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          대시보드로 돌아가기
        </Button>
      </Link>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <div
              className="h-4 w-4 rounded"
              style={{ backgroundColor: subject.color || "#6B7280" }}
            />
            <h1 className="text-3xl font-bold">{subject.name}</h1>
          </div>
          {subject.description && (
            <p className="mt-2 text-gray-600">{subject.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Link href={`/dashboard/subjects/${subjectId}/exams`}>
            <Button variant="outline">
              <ClipboardList className="mr-2 h-4 w-4" />
              시험 목록
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

