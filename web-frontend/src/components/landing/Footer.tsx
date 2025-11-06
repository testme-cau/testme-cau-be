'use client';

import { Github, Twitter, Linkedin, Mail } from 'lucide-react';
import Link from 'next/link';

export function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { name: '기능', href: '#features' },
      { name: '가격', href: '#pricing' },
      { name: 'FAQ', href: '#faq' },
      { name: '데모', href: '#demo' },
    ],
    company: [
      { name: '소개', href: '#about' },
      { name: '블로그', href: '#blog' },
      { name: '채용', href: '#careers' },
      { name: '연락처', href: '#contact' },
    ],
    legal: [
      { name: '개인정보처리방침', href: '#privacy' },
      { name: '이용약관', href: '#terms' },
      { name: '쿠키 정책', href: '#cookies' },
    ],
  };

  const socialLinks = [
    { name: 'GitHub', icon: Github, href: 'https://github.com' },
    { name: 'Twitter', icon: Twitter, href: 'https://twitter.com' },
    { name: 'LinkedIn', icon: Linkedin, href: 'https://linkedin.com' },
    { name: 'Email', icon: Mail, href: 'mailto:contact@testme.com' },
  ];

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-16">
        {/* Main footer content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-12">
          {/* Brand section */}
          <div className="lg:col-span-2">
            <Link href="/" className="inline-block mb-4">
              <h3 className="text-2xl font-bold text-white">test.me</h3>
            </Link>
            <p className="text-gray-400 mb-6 leading-relaxed max-w-sm">
              AI가 도와주는 스마트한 시험 제작 플랫폼.
              <br />
              시험 만들기, 이제 쉽게!
            </p>
            {/* Social links */}
            <div className="flex gap-4">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-10 h-10 rounded-full bg-gray-800 hover:bg-primary-600 flex items-center justify-center transition-colors duration-300"
                    aria-label={social.name}
                  >
                    <Icon className="w-5 h-5" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Product links */}
          <div>
            <h4 className="text-white font-semibold mb-4">제품</h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="hover:text-primary-400 transition-colors duration-200"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company links */}
          <div>
            <h4 className="text-white font-semibold mb-4">회사</h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="hover:text-primary-400 transition-colors duration-200"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal links */}
          <div>
            <h4 className="text-white font-semibold mb-4">법적 고지</h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="hover:text-primary-400 transition-colors duration-200"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">
              © {currentYear} test.me. All rights reserved.
            </p>
            <p className="text-sm text-gray-400">
              Made with 💚 by test.me team
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

