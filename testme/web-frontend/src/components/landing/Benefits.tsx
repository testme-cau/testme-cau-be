'use client';

import { motion } from 'framer-motion';
import { Clock, Target, Sliders, TrendingUp } from 'lucide-react';
import { useTranslations } from 'next-intl';

const iconConfigs = [
  { icon: Clock, gradient: 'from-primary-500 to-primary-600' },
  { icon: Target, gradient: 'from-secondary-500 to-secondary-600' },
  { icon: Sliders, gradient: 'from-accent-500 to-accent-600' },
  { icon: TrendingUp, gradient: 'from-primary-600 to-secondary-500' },
];

type BenefitContent = {
  stat: string;
  label: string;
  description: string;
};

export function Benefits() {
  const t = useTranslations('landing.benefits');
  const benefits = (t.raw('items') as BenefitContent[]) || [];

  return (
    <section id="benefits" className="py-24 bg-gradient-to-br from-gray-50 to-gray-100">
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
            {t('title')}
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {t('subtitle')}
          </p>
        </motion.div>

        {/* Benefits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {benefits.map((benefit, index) => {
            const { icon: Icon, gradient } = iconConfigs[index % iconConfigs.length];
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
                  <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${gradient} mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Stat */}
                  <div className={`text-5xl font-bold mb-2 bg-gradient-to-r ${gradient} text-transparent bg-clip-text`}>
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
                <div className={`absolute -z-10 inset-0 bg-gradient-to-br ${gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-300`}></div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

