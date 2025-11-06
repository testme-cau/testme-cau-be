'use client';

import { motion } from 'framer-motion';
import { Upload, Sparkles, CheckCheck } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Upload,
    title: 'PDF 업로드',
    description: '강의 자료나 교재를 PDF로 업로드하세요. 간단하게 드래그 앤 드롭!',
    color: 'from-primary-500 to-primary-600',
  },
  {
    number: '02',
    icon: Sparkles,
    title: 'AI가 시험 생성',
    description: 'GPT-5 또는 Gemini AI가 PDF를 분석하고, 맞춤형 시험 문제를 자동으로 만들어드려요.',
    color: 'from-secondary-500 to-secondary-600',
  },
  {
    number: '03',
    icon: CheckCheck,
    title: '자동 채점 & 결과 확인',
    description: '학생 답안을 AI가 채점하고, 상세한 피드백과 함께 결과를 제공해요.',
    color: 'from-accent-500 to-accent-600',
  },
];

export function HowItWorks() {
  return (
    <section className="py-24 bg-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary-50/30 to-transparent"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            어떻게 작동하나요?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            단 3단계로 시험 제작부터 채점까지 완성!
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative max-w-5xl mx-auto">
          {/* Connection line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-primary-200 via-secondary-200 to-accent-200 transform -translate-y-1/2 z-0"></div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 lg:gap-8">
            {steps.map((step, index) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                  className="relative"
                >
                  {/* Card */}
                  <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 relative z-10 group">
                    {/* Number badge */}
                    <div className={`absolute -top-6 -left-6 w-16 h-16 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      {step.number}
                    </div>

                    {/* Icon */}
                    <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${step.color} mb-6 mt-8 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>

                    {/* Title */}
                    <h3 className="text-2xl font-bold text-gray-900 mb-4">
                      {step.title}
                    </h3>

                    {/* Description */}
                    <p className="text-gray-600 leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  {/* Connection arrow (mobile) */}
                  {index < steps.length - 1 && (
                    <div className="lg:hidden flex justify-center my-6">
                      <div className="w-1 h-12 bg-gradient-to-b from-primary-300 to-secondary-300 rounded-full"></div>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Bottom CTA hint */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-16"
        >
          <p className="text-lg text-gray-500">
            지금 바로 시작해보세요! 🚀
          </p>
        </motion.div>
      </div>
    </section>
  );
}

