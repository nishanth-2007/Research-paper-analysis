import React from 'react';
import { AlertCircle, AlertTriangle, ShieldCheck, ArrowRight } from 'lucide-react';
import { IssueTier } from '../types';

interface MetricCounterCardsProps {
  blockersCount: number;
  improvementsCount: number;
  checksCount: number;
  activeTier: string;
  onSelectTier: (tier: IssueTier | 'all') => void;
}

export const MetricCounterCards: React.FC<MetricCounterCardsProps> = ({
  blockersCount,
  improvementsCount,
  checksCount,
  activeTier,
  onSelectTier,
}) => {
  const cards = [
    {
      tier: 'submission_blocker' as IssueTier,
      label: 'Submission Blockers',
      count: blockersCount,
      description: 'Critical guideline violations that risk immediate desk rejection.',
      icon: AlertCircle,
      accentBorder: 'border-rose-500/40 hover:border-rose-500/70',
      activeRing: 'ring-2 ring-rose-500/60 bg-rose-950/20',
      badgeBg: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
      countColor: 'text-rose-400',
    },
    {
      tier: 'improvement_recommended' as IssueTier,
      label: 'Recommended Improvements',
      count: improvementsCount,
      description: 'Key structural, formatting, or methodological enhancements.',
      icon: AlertTriangle,
      accentBorder: 'border-amber-500/40 hover:border-amber-500/70',
      activeRing: 'ring-2 ring-amber-500/60 bg-amber-950/20',
      badgeBg: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      countColor: 'text-amber-400',
    },
    {
      tier: 'check_or_limitation' as IssueTier,
      label: 'Checks & Limitations',
      count: checksCount,
      description: 'Informational considerations and extraction boundaries.',
      icon: ShieldCheck,
      accentBorder: 'border-indigo-500/40 hover:border-indigo-500/70',
      activeRing: 'ring-2 ring-indigo-500/60 bg-indigo-950/20',
      badgeBg: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
      countColor: 'text-indigo-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      {cards.map((card) => {
        const Icon = card.icon;
        const isActive = activeTier === card.tier;

        return (
          <div
            key={card.tier}
            onClick={() => onSelectTier(card.tier)}
            className={`glass-panel rounded-xl p-5 border cursor-pointer transition-all duration-200 group relative overflow-hidden ${
              card.accentBorder
            } ${isActive ? card.activeRing : 'hover:bg-slate-900/60'}`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2.5">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${card.badgeBg}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <h4 className="text-sm font-bold text-white font-heading">
                  {card.label}
                </h4>
              </div>
              <span className={`text-2xl font-black font-heading ${card.countColor}`}>
                {card.count}
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              {card.description}
            </p>

            <div className="flex items-center text-xs font-medium text-slate-300 group-hover:text-white transition-colors gap-1">
              <span>Filter action items</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        );
      })}
    </div>
  );
};
