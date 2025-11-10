"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useToast } from "@/hooks/use-toast";
import { generateExam } from "@/lib/api/exams";
import { getPDFs } from "@/lib/api/pdfs";
import { ExamGenerationRequest, PDF } from "@/types/api";
import { ArrowLeft, Loader2, FileText, CheckSquare, Square } from "lucide-react";

export default function GenerateExamPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;
  const pdfId = params.pdfId as string;

  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [loadingPdfs, setLoadingPdfs] = useState(true);
  const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([pdfId]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ExamGenerationRequest>({
    pdf_ids: [pdfId],
    num_questions: 10,
    difficulty: "medium",
    ai_provider: "gpt",
  });

  useEffect(() => {
    loadPdfs();
  }, [subjectId]);

  const loadPdfs = async () => {
    try {
      const data = await getPDFs(subjectId);
      setPdfs(data || []);
    } catch (error: any) {
      toast({
        title: "PDF 목록 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoadingPdfs(false);
    }
  };

  const handlePdfToggle = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedPdfIds((prev) => [...prev, id]);
    } else {
      setSelectedPdfIds((prev) => prev.filter((pId) => pId !== id));
    }
  };

  const handleSelectAll = () => {
    if (selectedPdfIds.length === pdfs.length) {
      setSelectedPdfIds([pdfId]); // Keep at least the initial PDF
    } else {
      setSelectedPdfIds(pdfs.map((pdf) => pdf.file_id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedPdfIds.length === 0) {
      toast({
        title: "PDF 선택 필요",
        description: "시험을 생성하려면 하나 이상의 PDF를 선택해야 합니다.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      const exam = await generateExam(subjectId, {
        ...formData,
        pdf_ids: selectedPdfIds,
      });
      toast({
        title: "시험 생성 완료",
        description: `${selectedPdfIds.length}개 PDF로부터 시험이 생성되었습니다.`,
      });
      router.push(`/dashboard/subjects/${subjectId}/exams/${exam.exam_id}`);
    } catch (error: any) {
      toast({
        title: "시험 생성 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="mx-auto max-w-2xl space-y-6">
          {/* Header */}
          <div>
            <Link href={`/dashboard/subjects/${subjectId}`}>
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                돌아가기
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">시험 생성</h1>
            <p className="mt-2 text-gray-600">
              AI가 PDF를 분석하여 자동으로 시험 문제를 생성합니다
            </p>
          </div>

          {/* PDF Selection */}
          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">PDF 선택</h2>
                <p className="text-sm text-gray-600">
                  시험에 포함할 PDF를 선택하세요 (최대 10개)
                </p>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
                disabled={loadingPdfs}
              >
                {selectedPdfIds.length === pdfs.length ? (
                  <>
                    <Square className="mr-2 h-4 w-4" />
                    전체 해제
                  </>
                ) : (
                  <>
                    <CheckSquare className="mr-2 h-4 w-4" />
                    전체 선택
                  </>
                )}
              </Button>
            </div>

            {loadingPdfs ? (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner size="lg" />
              </div>
            ) : (
              <div className="space-y-2">
                <div className="mb-3 rounded-lg bg-blue-50 p-3">
                  <p className="text-sm text-blue-900">
                    <strong>{selectedPdfIds.length}개 PDF 선택됨</strong>
                  </p>
                  {selectedPdfIds.length > 1 && (
                    <p className="mt-1 text-xs text-blue-700">
                      여러 PDF의 내용을 종합하여 시험이 생성됩니다
                    </p>
                  )}
                </div>
                
                {pdfs.map((pdf) => (
                  <div
                    key={pdf.file_id}
                    className="flex items-center gap-3 rounded-lg border p-3 hover:bg-gray-50"
                  >
                    <Checkbox
                      checked={selectedPdfIds.includes(pdf.file_id)}
                      onCheckedChange={(checked) =>
                        handlePdfToggle(pdf.file_id, checked as boolean)
                      }
                    />
                    <FileText className="h-5 w-5 text-gray-400" />
                    <div className="flex-1">
                      <p className="font-medium">{pdf.original_filename}</p>
                      <p className="text-sm text-gray-500">
                        {(pdf.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    {pdf.file_id === pdfId && (
                      <span className="rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800">
                        선택한 PDF
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Form */}
          <Card>
            <form onSubmit={handleSubmit} className="space-y-6 p-6">
              {/* Number of Questions */}
              <div>
                <Label htmlFor="num_questions">문제 수</Label>
                <div className="mt-2">
                  <input
                    type="range"
                    id="num_questions"
                    min="1"
                    max="50"
                    value={formData.num_questions}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        num_questions: parseInt(e.target.value),
                      })
                    }
                    className="w-full"
                    disabled={loading}
                  />
                  <div className="mt-2 flex justify-between text-sm text-gray-600">
                    <span>1문제</span>
                    <span className="font-semibold text-primary">
                      {formData.num_questions}문제
                    </span>
                    <span>50문제</span>
                  </div>
                </div>
              </div>

              {/* Difficulty */}
              <div>
                <Label htmlFor="difficulty">난이도</Label>
                <Select
                  value={formData.difficulty}
                  onValueChange={(value: "easy" | "medium" | "hard") =>
                    setFormData({ ...formData, difficulty: value })
                  }
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="easy">쉬움</SelectItem>
                    <SelectItem value="medium">보통</SelectItem>
                    <SelectItem value="hard">어려움</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* AI Provider */}
              <div>
                <Label htmlFor="ai_provider">AI 제공자</Label>
                <Select
                  value={formData.ai_provider}
                  onValueChange={(value: "gpt" | "gemini") =>
                    setFormData({ ...formData, ai_provider: value })
                  }
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt">GPT-5</SelectItem>
                    <SelectItem value="gemini">Gemini 1.5 Pro</SelectItem>
                  </SelectContent>
                </Select>
                <p className="mt-1 text-sm text-gray-500">
                  시험 생성에 사용할 AI 모델을 선택하세요
                </p>
              </div>

              {/* Estimated Time */}
              <div className="rounded-lg bg-blue-50 p-4">
                <p className="text-sm text-blue-900">
                  <strong>예상 소요 시간:</strong>{" "}
                  {Math.ceil(formData.num_questions * 2)} 분
                </p>
                <p className="mt-1 text-xs text-blue-700">
                  AI가 PDF를 분석하고 문제를 생성하는 데 시간이 걸릴 수 있습니다.
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <Button type="submit" disabled={loading} className="w-full">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      생성 중... (잠시만 기다려주세요)
                    </>
                  ) : (
                    "시험 생성"
                  )}
                </Button>
              </div>
            </form>
          </Card>

          {/* Info */}
          <Card className="p-6">
            <h3 className="font-semibold">💡 팁</h3>
            <ul className="mt-2 space-y-2 text-sm text-gray-600">
              <li>• PDF 내용이 많을수록 더 다양한 문제가 생성됩니다</li>
              <li>• 난이도에 따라 문제의 복잡도가 조정됩니다</li>
              <li>• 객관식과 주관식 문제가 자동으로 생성됩니다</li>
            </ul>
          </Card>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}

