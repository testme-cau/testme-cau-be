'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/ui/logo';
import Link from 'next/link';

export function Navigation() {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="group">
            <Logo size="md" />
            <div className="h-0.5 w-0 bg-gradient-to-r from-emerald-600 to-teal-600 group-hover:w-full transition-all duration-300"></div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              href="#features"
              className="text-gray-600 hover:text-emerald-600 transition-colors duration-200 font-medium"
            >
              특징
            </Link>
            <Link
              href="#benefits"
              className="text-gray-600 hover:text-emerald-600 transition-colors duration-200 font-medium"
            >
              장점
            </Link>
            <Link
              href="#how-it-works"
              className="text-gray-600 hover:text-emerald-600 transition-colors duration-200 font-medium"
            >
              사용방법
            </Link>
          </div>

          {/* CTA Button */}
          <div className="flex items-center space-x-4">
                <Link href="/login">
                  <Button className="bg-emerald-600 hover:bg-emerald-700 text-white shadow-md hover:shadow-lg transition-all duration-300">
                    시작하기
                  </Button>
                </Link>
          </div>
        </div>
      </div>
    </motion.nav>
  );
}

