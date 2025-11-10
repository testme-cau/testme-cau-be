'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/ui/logo';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';

export function Navigation() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // 화면 높이의 50% 이상 스크롤하면 헤더 표시
      const scrollPosition = window.scrollY;
      const triggerHeight = window.innerHeight * 0.5;
      setIsVisible(scrollPosition > triggerHeight);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
    <motion.nav
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
              <Link href="/">
                <div className="group cursor-pointer">
            <Logo size="md" />
            <div className="h-0.5 w-0 bg-gradient-to-r from-primary-600 to-secondary-600 group-hover:w-full transition-all duration-300"></div>
          </div>
              </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
                <button
                  onClick={() => {
                    const element = document.getElementById('features');
                    element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200 font-medium"
            >
              특징
                </button>
                <button
                  onClick={() => {
                    const element = document.getElementById('benefits');
                    element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200 font-medium"
            >
              장점
                </button>
                <button
                  onClick={() => {
                    const element = document.getElementById('how-it-works');
                    element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
              className="text-gray-600 hover:text-primary-600 transition-colors duration-200 font-medium"
            >
              사용방법
                </button>
          </div>

              {/* CTA Button - 스크롤 시 Hero에서 이동 */}
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.3 }}
                className="flex items-center space-x-4"
              >
                <Link href="/login">
                  <Button 
                    size="lg"
                    className="bg-primary-600 hover:bg-primary-700 text-white shadow-md hover:shadow-lg transition-all duration-300 group"
                  >
                    시작하기
                    <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
              </motion.div>
        </div>
      </div>
    </motion.nav>
      )}
    </AnimatePresence>
  );
}

