'use client';

import { motion } from 'framer-motion';
import { Clock, Target, Sliders, TrendingUp } from 'lucide-react';

const benefits = [
  {
    icon: Clock,
    stat: '90%',
    label: '시간 절약',
    description: '수동 작업 대비 90% 시간을 단축하세요',
    gradient: 'from-primary-500 to-primary-600',
  },
  {
    icon: Target,
    stat: '99%',
    label: '정확도',
    description: 'AI 기반 일관된 평가로 공정한 채점',
    gradient: 'from-secondary-500 to-secondary-600',
  },
  {
    icon: Sliders,
    stat: '무한',
    label: '맞춤화',
    description: '난이도별로 원하는 문제를 자유롭게',
    gradient: 'from-accent-500 to-accent-600',
  },
  {
    icon: TrendingUp,
    stat: '무제한',
    label: '확장성',
    description: '제한 없이 시험을 생성하고 관리',
    gradient: 'from-primary-600 to-secondary-500',
  },
];

export function Benefits() {
  return (
    <section className="py-24 bg-gradient-to-br from-gray-50 to-gray-100">
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
            왜 test.me일까요?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            시간도 절약하고, 품질도 높이는 스마트한 선택
          </p>
        </motion.div>

        {/* Benefits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {benefits.map((benefit, index) => {
            const Icon = benefit.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="relative group"
              >
                {/* Card */}
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 h-full">
                  {/* Icon */}
                  <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${benefit.gradient} mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Stat */}
                  <div className={`text-5xl font-bold mb-2 bg-gradient-to-r ${benefit.gradient} text-transparent bg-clip-text`}>
                    {benefit.stat}
                  </div>

                  {/* Label */}
                  <h3 className="text-xl font-bold text-gray-900 mb-3">
                    {benefit.label}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 leading-relaxed">
                    {benefit.description}
                  </p>
                </div>

                {/* Decorative element */}
                <div className={`absolute -z-10 inset-0 bg-gradient-to-br ${benefit.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-300`}></div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

