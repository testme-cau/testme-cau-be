'use client';

import { Github, Twitter, Linkedin, Mail } from 'lucide-react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';

export function Footer() {
  const currentYear = new Date().getFullYear();
  const t = useTranslations('landing.footer');
  const navT = useTranslations('landing.nav');

  const socialLinks = [
    { name: 'GitHub', icon: Github, href: 'https://github.com' },
    { name: 'Twitter', icon: Twitter, href: 'https://twitter.com' },
    { name: 'LinkedIn', icon: Linkedin, href: 'https://linkedin.com' },
    { name: 'Email', icon: Mail, href: 'mailto:contact@testme.com' },
  ];

  const quickLinks = [
    { label: navT('features'), href: '#features' },
    { label: navT('benefits'), href: '#benefits' },
    { label: navT('about'), href: '#how-it-works' },
  ];

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-16">
        {/* Main footer content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Brand section */}
          <div className="lg:col-span-2">
            <Link href="/" className="inline-block mb-4">
              <h3 className="text-2xl font-bold text-white">test.me</h3>
            </Link>
            <p className="text-gray-400 mb-6 leading-relaxed max-w-sm">
              {t('description')}
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

          {/* Quick links */}
          <div>
            <h4 className="text-white font-semibold mb-4">{navT('product')}</h4>
            <ul className="space-y-3">
              {quickLinks.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="hover:text-primary-400 transition-colors duration-200"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal links */}
          <div>
            <h4 className="text-white font-semibold mb-4">{t('privacy')}</h4>
            <ul className="space-y-3">
              <li>
                <Link href="#privacy" className="hover:text-primary-400 transition-colors duration-200">
                  {t('privacy')}
                </Link>
              </li>
              <li>
                <Link href="#terms" className="hover:text-primary-400 transition-colors duration-200">
                  {t('terms')}
                </Link>
              </li>
              <li>
                <Link href="mailto:contact@testme.com" className="hover:text-primary-400 transition-colors duration-200">
                  {t('contact')}
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">
              {t('rights', { year: currentYear })}
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

