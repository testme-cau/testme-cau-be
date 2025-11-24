import { redirect } from "next/navigation";

interface ExamsPageProps {
  params: {
    subjectId: string;
  };
}

export default function ExamsPageRedirect({ params }: ExamsPageProps) {
  redirect(`/dashboard/subjects/${params.subjectId}?tab=exams`);
}