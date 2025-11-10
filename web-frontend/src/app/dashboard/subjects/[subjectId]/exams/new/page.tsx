"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import { generateExam } from "@/lib/api/exams";
import { getPDFs } from "@/lib/api/pdfs";
import { PDF, ExamGenerationRequest } from "@/types/api";
import { ArrowLeft, Loader2, FileText } from "lucide-react";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

export default function NewExamPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;

  const [loading, setLoading] = useState(false);
  const [pdfsLoading, setPdfsLoading] = useState(true);
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([]);
  const [formData, setFormData] = useState({
    num_questions: 10,
    difficulty: "medium" as "easy" | "medium" | "hard",
    ai_provider: "gpt" as "gpt" | "gemini",
  });

  useEffect(() => {
    loadPDFs();
  }, []);

  const loadPDFs = async () => {
    try {
      const pdfsData = await getPDFs(subjectId);
      setPdfs(pdfsData);
    } catch (error: any) {
      toast({
        title: "PDF 목록 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setPdfsLoading(false);
    }
  };

  const handlePdfToggle = (pdfId: string) => {
    setSelectedPdfIds((prev) =>
      prev.includes(pdfId)
        ? prev.filter((id) => id !== pdfId)
        : [...prev, pdfId]
    );
  };

  const handleSelectAll = () => {
    if (selectedPdfIds.length === pdfs.length) {
      setSelectedPdfIds([]);
    } else {
      setSelectedPdfIds(pdfs.map((pdf) => pdf.file_id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedPdfIds.length === 0) {
      toast({
        title: "PDF 선택 필요",
        description: "최소 1개의 PDF를 선택해주세요.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      // For now, use the first selected PDF (multi-PDF support coming soon)
      const request: ExamGenerationRequest = {
        pdf_id: selectedPdfIds[0],
        num_questions: formData.num_questions,
        difficulty: formData.difficulty,
        ai_provider: formData.ai_provider,
      };

      const exam = await generateExam(subjectId, request);
      toast({
        title: "시험 생성 완료",
        description: "AI가 시험을 성공적으로 생성했습니다.",
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

  if (pdfsLoading) {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="mx-auto max-w-3xl space-y-6">
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

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* PDF Selection */}
            <Card className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-semibold">PDF 선택</Label>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleSelectAll}
                    disabled={loading || pdfs.length === 0}
                  >
                    {selectedPdfIds.length === pdfs.length
                      ? "전체 해제"
                      : "전체 선택"}
                  </Button>
                </div>

                {pdfs.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
                    <FileText className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-4 text-sm font-semibold text-gray-900">
                      업로드된 PDF가 없습니다
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      먼저 PDF를 업로드해주세요.
                    </p>
                    <Link href={`/dashboard/subjects/${subjectId}`}>
                      <Button className="mt-4" variant="outline">
                        과목 페이지로 이동
                      </Button>
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {pdfs.map((pdf) => (
                      <div
                        key={pdf.file_id}
                        className={`flex items-start gap-3 rounded-lg border p-4 transition-all ${
                          selectedPdfIds.includes(pdf.file_id)
                            ? "border-emerald-500 bg-emerald-50"
                            : "border-gray-200 hover:bg-gray-50"
                        }`}
                      >
                        <Checkbox
                          id={pdf.file_id}
                          checked={selectedPdfIds.includes(pdf.file_id)}
                          onCheckedChange={() => handlePdfToggle(pdf.file_id)}
                          disabled={loading}
                          className="mt-1"
                        />
                        <label
                          htmlFor={pdf.file_id}
                          className="flex-1 cursor-pointer"
                        >
                          <div className="font-medium text-gray-900">
                            {pdf.original_filename}
                          </div>
                          <div className="mt-1 text-xs text-gray-500">
                            {(pdf.size / 1024 / 1024).toFixed(2)} MB •{" "}
                            {new Date(pdf.uploaded_at).toLocaleDateString(
                              "ko-KR"
                            )}
                          </div>
                        </label>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-sm text-gray-500">
                  ✨ <strong>{selectedPdfIds.length}개</strong>의 PDF 선택됨
                  {selectedPdfIds.length > 1 && (
                    <span className="text-amber-600">
                      {" "}
                      (현재는 첫 번째 PDF만 사용됩니다. 다중 PDF 지원 예정)
                    </span>
                  )}
                </p>
              </div>
            </Card>

            {/* Exam Options */}
            <Card className="p-6">
              <div className="space-y-6">
                <h3 className="text-base font-semibold">시험 옵션</h3>

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
                      <span className="font-semibold text-emerald-600">
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
              </div>
            </Card>

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
              <Button
                type="submit"
                disabled={loading || selectedPdfIds.length === 0}
                className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
              >
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

