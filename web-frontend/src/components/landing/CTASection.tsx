'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Users } from 'lucide-react';
import Link from 'next/link';

export function CTASection() {
  return (
    <section className="py-24 bg-gradient-to-br from-primary-600 via-primary-500 to-secondary-600 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden opacity-20">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-white rounded-full mix-blend-overlay filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-white rounded-full mix-blend-overlay filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center"
        >
          {/* Main message */}
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
            시험 만들기,
            <br />
            이제는 더 쉽게!
          </h2>

          <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-2xl mx-auto">
            AI가 도와주는 스마트한 시험 제작, 지금 무료로 시작하세요
          </p>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12"
          >
            <Link href="/login">
              <Button 
                size="lg" 
                className="bg-white text-primary-700 hover:bg-gray-50 shadow-2xl hover:shadow-3xl transition-all duration-300 group px-10 py-7 text-lg font-semibold"
              >
                지금 시작하기
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </motion.div>

          {/* Social proof */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex items-center justify-center gap-3 text-white/80"
          >
            <Users className="w-5 h-5" />
            <p className="text-lg">
              이미 <span className="font-bold text-white">1,000명+</span>이 사용 중이에요
            </p>
          </motion.div>

          {/* Additional info */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-8 text-white/70 text-sm"
          >
            신용카드 등록 없이 바로 시작 · 언제든 취소 가능
          </motion.div>
        </motion.div>
      </div>

      <style jsx>{`
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </section>
  );
}

