"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { getSupportedLanguages } from "@/lib/api/user";
import { cn } from "@/lib/utils";
import { LanguageOption } from "@/types/api";

interface ExamLanguageSelectProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  className?: string;
}

export function ExamLanguageSelect({
  value,
  onChange,
  disabled,
  className,
}: ExamLanguageSelectProps) {
  const { toast } = useToast();
  const [languages, setLanguages] = useState<LanguageOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        setLoading(true);
        const list = await getSupportedLanguages();
        if (!mounted) return;
        setLanguages(list);
      } catch (error: any) {
        if (!mounted) return;
        toast({
          title: "언어 목록을 불러오지 못했습니다",
          description: error?.message || "잠시 후 다시 시도해주세요.",
          variant: "destructive",
        });
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    load();
    return () => {
      mounted = false;
    };
  }, [toast]);

  useEffect(() => {
    if (loading || languages.length === 0) return;
    const exists = languages.some(
      (languageOption) =>
        languageOption.code.toLowerCase() === value?.toLowerCase()
    );
    if (!exists) {
      onChange(languages[0].code);
    }
  }, [languages, loading, onChange, value]);

  return (
    <div className={cn("space-y-2", className)}>
      <Label className="text-sm font-semibold">출제 언어</Label>
      {loading ? (
        <div className="flex items-center gap-2 rounded-md border border-dashed border-gray-200 px-3 py-2 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin text-emerald-500" />
          언어 목록을 불러오는 중입니다...
        </div>
      ) : (
        <Select
          value={value}
          onValueChange={onChange}
          disabled={disabled || loading || languages.length === 0}
        >
          <SelectTrigger className="w-full h-auto min-h-[48px] py-2">
            <SelectValue placeholder="언어를 선택하세요" />
          </SelectTrigger>
          <SelectContent className="p-2">
            {languages.map((languageOption) => (
              <SelectItem
                key={languageOption.code}
                value={languageOption.code}
                textValue={`${languageOption.flag ?? ""} ${languageOption.native_name} (${languageOption.name})`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{languageOption.flag}</span>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">
                      {languageOption.native_name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {languageOption.name}
                    </span>
                  </div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
      <p className="text-xs text-gray-500">
        선택한 언어로 문제와 해설, 채점 피드백이 생성됩니다.
      </p>
    </div>
  );
}

