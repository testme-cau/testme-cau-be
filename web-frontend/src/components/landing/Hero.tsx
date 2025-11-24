'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/ui/logo';
import { ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { fetchBetaStatus } from '@/lib/api/system';
import type { BetaStatusResponse } from '@/types/api';
import { useTranslations } from 'next-intl';

export function Hero() {
  const [ctaOpacity, setCtaOpacity] = useState(1);
  const [betaStatus, setBetaStatus] = useState<BetaStatusResponse | null>(null);
  const t = useTranslations('landing.hero');

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const triggerHeight = window.innerHeight * 0.3;
      // 스크롤 시 CTA 버튼 페이드아웃 (0.3vh ~ 0.5vh 사이에서)
      const opacity = Math.max(0, 1 - (scrollPosition - triggerHeight * 0.7) / (triggerHeight * 0.8));
      setCtaOpacity(opacity);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    fetchBetaStatus()
      .then(setBetaStatus)
      .catch(() => {
        // 노출 실패 시 조용히 무시 (랜딩은 항상 접근 가능해야 함)
      });
  }, []);

  const isClosedBeta = betaStatus?.status === 'closed_beta';

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-brand-gradient">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-accent-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Large Logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="mb-12 flex justify-center"
          >
            <div className="transform scale-[2.5] mb-8">
              <Logo size="lg" />
            </div>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight"
          >
            {t('titlePrimary')}
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-secondary-600">
              {t('titleHighlight')}
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-xl md:text-2xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed"
          >
            {t.rich('subtitle', {
              br: () => <br />,
            })}
          </motion.p>

          {isClosedBeta && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45, duration: 0.4 }}
              className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white/80 text-amber-600 border border-amber-200 shadow-sm mb-6"
            >
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-semibold">{t('betaBadge')}</span>
            </motion.div>
          )}

          {/* CTA Buttons - 스크롤 시 페이드아웃 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            style={{ opacity: ctaOpacity }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link href="/login">
              <Button 
                size="lg" 
                className="bg-primary-600 hover:bg-primary-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 group px-8 py-6 text-lg"
              >
                {t('cta')}
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>

          {/* Social Proof */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="mt-12 flex items-center justify-center gap-6 text-sm text-gray-500"
          >
            <div className="flex -space-x-2">
              <div className="w-8 h-8 rounded-full bg-primary-200 border-2 border-white"></div>
              <div className="w-8 h-8 rounded-full bg-secondary-200 border-2 border-white"></div>
              <div className="w-8 h-8 rounded-full bg-accent-200 border-2 border-white"></div>
              <div className="w-8 h-8 rounded-full bg-primary-300 border-2 border-white flex items-center justify-center text-xs font-medium">
                +
              </div>
            </div>
            <p>
              {t.rich('usage', {
                strong: (chunks) => (
                  <span className="font-semibold text-gray-700">{chunks}</span>
                ),
                count: '1,000',
              })}
            </p>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.6 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-primary-300 rounded-full flex justify-center"
        >
          <motion.div className="w-1.5 h-2 bg-primary-500 rounded-full mt-2"></motion.div>
        </motion.div>
      </motion.div>

      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </section>
  );
}

