import React, { useState } from 'react';
import { AlertTriangle, X, ShieldAlert, Info } from 'lucide-react';
import { DocumentValidation } from '../types';

interface ValidationAlertBannerProps {
  validation: DocumentValidation | null | undefined;
  isProvisional: boolean;
  provisionalReason?: string | null;
}

export const ValidationAlertBanner: React.FC<ValidationAlertBannerProps> = ({
  validation,
  isProvisional,
  provisionalReason,
}) => {
  const [dismissed, setDismissed] = useState(false);

  // If not provisional and validation is plausible, don't show
  if (dismissed) return null;
  if (!isProvisional && (!validation || validation.is_plausible_manuscript)) return null;

  const docTypeLabel = validation?.document_type
    ? validation.document_type.replace(/_/g, ' ').toUpperCase()
    : 'NON-JOURNAL DOCUMENT';

  const message =
    validation?.warning_message ||
    provisionalReason ||
    'The uploaded document does not match standard research manuscript structure. Journal readiness checks were marked provisional and deductions suspended to avoid false penalties.';

  return (
    <div className="rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 relative overflow-hidden backdrop-blur-md text-amber-200">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                PROVISIONAL AUDIT: {docTypeLabel}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-amber-200/90 mt-1.5 leading-relaxed">
              {message}
            </p>
            <div className="mt-2 flex items-center gap-1.5 text-[11px] text-amber-400/80">
              <Info className="w-3.5 h-3.5 flex-shrink-0" />
              <span>
                To receive definitive journal readiness scoring, please upload a formatted research manuscript containing standard IMRAD sections.
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setDismissed(true)}
          className="text-amber-400 hover:text-amber-200 p-1 rounded-lg hover:bg-amber-900/40 transition-colors flex-shrink-0"
          title="Dismiss notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
