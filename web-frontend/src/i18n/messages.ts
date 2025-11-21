import type { Locale } from "./config";
import ko from "./locales/ko.json";
import en from "./locales/en.json";
import ja from "./locales/ja.json";

export type Messages = Record<string, any>;

export const messagesByLocale: Record<Locale, Messages> = {
  ko,
  en,
  ja,
};


