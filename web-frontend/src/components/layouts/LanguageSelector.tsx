"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Globe, Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import type { LanguageOption, UserProfile } from "@/types/api";
import {
  getSupportedLanguages,
  getUserProfile,
  updateUserProfile,
} from "@/lib/api/user";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { useApiRequest } from "@/hooks/useApiRequest";
import { cn } from "@/lib/utils";
import {
  defaultLocale,
  isSupportedLocale,
  Locale,
  supportedLocales,
} from "@/i18n/config";
import { messagesByLocale } from "@/i18n/messages";
import { useLocaleStore } from "@/store/localeStore";

interface LanguageSelectorProps {
  className?: string;
}

export function LanguageSelector({ className }: LanguageSelectorProps) {
  const { user, loading: authLoading } = useAuth();
  const { toast } = useToast();
  const { execute: executeUpdate, loading: updating } = useApiRequest<UserProfile>();
  const t = useTranslations("language");
  const storeLocale = useLocaleStore((state) => state.locale);
  const setLocale = useLocaleStore((state) => state.setLocale);
  const setMessages = useLocaleStore((state) => state.setMessages);

  const [languages, setLanguages] = useState<LanguageOption[]>([]);
  const [value, setValue] = useState<string>("ko");
  const [initializing, setInitializing] = useState(true);
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      setInitializing(false);
      return;
    }

    let cancelled = false;

    const load = async () => {
      try {
        setInitializing(true);
        const [languageList, profile] = await Promise.all([
          getSupportedLanguages(),
          getUserProfile(),
        ]);
        if (cancelled) return;
        const filteredLanguages = supportedLocales
          .map((code) =>
            languageList.find(
              (lang) => lang.code.toLowerCase() === code.toLowerCase()
            )
          )
          .filter((lang): lang is LanguageOption => Boolean(lang));
        setLanguages(filteredLanguages);
        const preferred =
          profile.language_preference && isSupportedLocale(profile.language_preference)
            ? (profile.language_preference as Locale)
            : defaultLocale;
        setValue(preferred);
      } catch (error: any) {
        if (cancelled) return;
        toast({
          title: t("loadError"),
          description: error.message,
          variant: "destructive",
        });
      } finally {
        if (!cancelled) {
          setInitializing(false);
        }
      }
    };

    load();

    return () => {
      cancelled = true;
    };
  }, [authLoading, user, toast, t]);

  useEffect(() => {
    if (!open) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (!menuRef.current) return;
      if (!menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  useEffect(() => {
    if (storeLocale && storeLocale !== value) {
      setValue(storeLocale);
    }
  }, [storeLocale, value]);

  const selectedLanguage = useMemo(
    () => languages.find((lang) => lang.code === value),
    [languages, value]
  );

  const handleLanguageChange = async (nextValue: string) => {
    if (!nextValue || nextValue === value) return;
    const previousValue = value;
    setValue(nextValue);

    const result = await executeUpdate(
      () => updateUserProfile({ language_preference: nextValue }),
      {
        errorMessage: t("changeError"),
      }
    );

    if (result === null) {
      setValue(previousValue);
    } else {
      if (isSupportedLocale(nextValue)) {
        const localeValue = nextValue as Locale;
        setLocale(localeValue);
        setMessages(messagesByLocale[localeValue]);
      }
      toast({
        title: t("changeSuccessTitle"),
        description: t("changeSuccessDescription"),
      });
      setOpen(false);
    }
  };

  if (initializing || !user || languages.length === 0) {
    return null;
  }

  return (
    <div className={cn("relative", className)} ref={menuRef}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        disabled={updating}
        className={cn(
          "flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-700 transition hover:bg-gray-50 disabled:opacity-50",
          updating && "cursor-not-allowed"
        )}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={
          selectedLanguage
            ? t("selectedLabel", { language: selectedLanguage.native_name })
            : t("selectLabel")
        }
      >
        {updating ? (
          <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
        ) : (
          <Globe className="h-5 w-5" />
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-64 rounded-xl border border-gray-200 bg-white shadow-lg">
          <div className="max-h-72 overflow-y-auto py-2">
            {languages.map((lang) => {
              const isActive = lang.code === value;
              return (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => handleLanguageChange(lang.code)}
                  className={cn(
                    "flex w-full items-center gap-3 px-4 py-2 text-left text-sm transition hover:bg-gray-50",
                    isActive && "bg-gray-100 font-semibold"
                  )}
                >
                  <span className="text-lg">{lang.flag}</span>
                  <div className="flex flex-col">
                    <span>{lang.native_name}</span>
                    <span className="text-xs text-gray-500">{lang.name}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

