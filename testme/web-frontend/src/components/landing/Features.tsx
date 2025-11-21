'use client';

import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Bot, CheckCircle, Zap } from 'lucide-react';
import { useTranslations } from 'next-intl';

const iconConfigs = [
  { icon: FileText, color: 'from-primary-500 to-primary-600' },
  { icon: Bot, color: 'from-secondary-500 to-secondary-600' },
  { icon: CheckCircle, color: 'from-accent-500 to-accent-600' },
  { icon: Zap, color: 'from-primary-600 to-secondary-500' },
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

type FeatureContent = {
  title: string;
  description: string;
};

export function Features() {
  const t = useTranslations('landing.features');
  const featureContent = (t.raw('items') as FeatureContent[]) || [];

  return (
    <section id="features" className="py-24 bg-white">
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

        {/* Features Grid */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {featureContent.map((feature, index) => {
            const { icon: Icon, color } = iconConfigs[index % iconConfigs.length];
            return (
              <motion.div key={index} variants={item}>
                <Card className="h-full border-0 shadow-lg hover:shadow-2xl transition-all duration-300 group cursor-pointer overflow-hidden relative">
                  {/* Gradient background on hover - Card 레벨로 이동 */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-secondary-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                    
                  <CardContent className="p-6 relative z-10">
                      {/* Icon with gradient */}
                      <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-br ${color} mb-4 group-hover:scale-110 transition-transform duration-300`}>
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

