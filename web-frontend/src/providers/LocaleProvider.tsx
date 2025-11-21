"use client";

import { ReactNode, useEffect } from "react";
import { NextIntlClientProvider } from "next-intl";
import { useLocaleStore } from "@/store/localeStore";
import { messagesByLocale } from "@/i18n/messages";
import {
  defaultLocale,
  defaultTimeZone,
  isSupportedLocale,
  Locale,
} from "@/i18n/config";
import { useAuth } from "@/hooks/useAuth";
import { getUserProfile } from "@/lib/api/user";

interface LocaleProviderProps {
  children: ReactNode;
}

export function LocaleProvider({ children }: LocaleProviderProps) {
  const { user, loading } = useAuth();
  const locale = useLocaleStore((state) => state.locale);
  const currentMessages = useLocaleStore((state) => state.messages);
  const setLocale = useLocaleStore((state) => state.setLocale);
  const setMessages = useLocaleStore((state) => state.setMessages);

  useEffect(() => {
    let cancelled = false;

    const applyLocale = (nextLocale: Locale) => {
      if (cancelled) return;
      setLocale(nextLocale);
      setMessages(messagesByLocale[nextLocale]);
      if (typeof document !== "undefined") {
        document.documentElement.lang = nextLocale;
      }
    };

    const syncLocale = async () => {
      if (loading) {
        return;
      }

      if (!user) {
        applyLocale(defaultLocale);
        return;
      }

      try {
        const profile = await getUserProfile();
        const preferred = profile.language_preference;
        if (isSupportedLocale(preferred)) {
          applyLocale(preferred);
        } else {
          applyLocale(defaultLocale);
        }
      } catch {
        applyLocale(defaultLocale);
      }
    };

    syncLocale();

    return () => {
      cancelled = true;
    };
  }, [user, loading, setLocale, setMessages]);

  return (
    <NextIntlClientProvider
      locale={locale ?? defaultLocale}
      messages={currentMessages ?? messagesByLocale[defaultLocale]}
      timeZone={defaultTimeZone}
    >
      {children}
    </NextIntlClientProvider>
  );
}


