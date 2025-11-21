"use client";

import { create } from "zustand";
import { Locale, defaultLocale } from "@/i18n/config";
import { messagesByLocale, Messages } from "@/i18n/messages";

interface LocaleState {
  locale: Locale;
  messages: Messages;
  setLocale: (locale: Locale) => void;
  setMessages: (messages: Messages) => void;
}

export const useLocaleStore = create<LocaleState>((set) => ({
  locale: defaultLocale,
  messages: messagesByLocale[defaultLocale],
  setLocale: (locale) => set({ locale }),
  setMessages: (messages) => set({ messages }),
}));


