export const supportedLocales = ["ko", "en", "ja"] as const;

export type Locale = (typeof supportedLocales)[number];

export const defaultLocale: Locale = "ko";

export const defaultTimeZone =
  process.env.NEXT_PUBLIC_I18N_TIMEZONE || "Asia/Seoul";

export function isSupportedLocale(locale?: string | null): locale is Locale {
  if (!locale) return false;
  return (supportedLocales as readonly string[]).includes(locale.toLowerCase());
}


