'use client';

import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Bot, CheckCircle, Zap } from 'lucide-react';

const features = [
  {
    icon: FileText,
    title: 'PDF 업로드만으로 시험 생성',
    description: '강의 자료 PDF를 업로드하면 AI가 자동으로 문제를 만들어드려요. 복잡한 설정은 필요 없어요!',
    color: 'from-primary-500 to-primary-600',
  },
  {
    icon: Bot,
    title: 'GPT-5 & Gemini 듀얼 AI 엔진',
    description: '최신 AI 기술로 더 정확하고 다양한 문제를 생성해요. 원하는 AI를 선택할 수 있어요!',
    color: 'from-secondary-500 to-secondary-600',
  },
  {
    icon: CheckCircle,
    title: '자동 채점 및 피드백',
    description: '학생 답안을 AI가 자동으로 채점하고, 상세한 피드백까지 제공해드려요.',
    color: 'from-accent-500 to-accent-600',
  },
  {
    icon: Zap,
    title: '실시간 결과 분석',
    description: '시험 결과를 실시간으로 확인하고, 학습 패턴을 분석해서 더 나은 문제를 만들어요.',
    color: 'from-primary-600 to-secondary-500',
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export function Features() {
  return (
    <section className="py-24 bg-white">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            강력한 기능들
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            시험 만들기부터 채점까지, 모든 과정을 자동화하세요
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div key={index} variants={item}>
                <Card className="h-full border-0 shadow-lg hover:shadow-2xl transition-all duration-300 group cursor-pointer overflow-hidden">
                  <CardContent className="p-6 relative">
                    {/* Gradient background on hover */}
                    <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-secondary-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    
                    <div className="relative z-10">
                      {/* Icon with gradient */}
                      <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-br ${feature.color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>

                      {/* Title */}
                      <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-primary-700 transition-colors">
                        {feature.title}
                      </h3>

                      {/* Description */}
                      <p className="text-gray-600 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}

