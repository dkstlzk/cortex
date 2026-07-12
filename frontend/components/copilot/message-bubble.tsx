'use client';

import { motion } from 'framer-motion';
import { Cpu, User, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';
import type { CopilotMessage } from '@/lib/types';
import { CitationChip } from './citation-chip';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: CopilotMessage;
  entityTag: string;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn('flex gap-3', isUser && 'flex-row-reverse')}
    >
      <div className={cn(
        'w-8 h-8 rounded-md flex items-center justify-center shrink-0 border',
        isUser
          ? 'bg-signal-soft border-signal/30 text-signal'
          : 'bg-mint-soft border-mint/30 text-mint',
      )}>
        {isUser ? <User className="w-4 h-4" /> : <Cpu className="w-4 h-4" />}
      </div>

      <div className={cn('max-w-[82%] space-y-2', isUser && 'text-right')}>
        <div className={cn(
          'inline-block text-left rounded-lg px-4 py-3 text-sm leading-relaxed border',
          isUser
            ? 'bg-signal text-base border-transparent rounded-tr-sm font-medium'
            : 'bg-panel text-ink border-line rounded-tl-sm',
        )}>
          {message.streaming && !message.content ? (
            <span className="inline-flex items-center gap-1 py-0.5">
              <span className="think-dot w-1.5 h-1.5 rounded-full bg-mint" style={{ animationDelay: '0ms' }} />
              <span className="think-dot w-1.5 h-1.5 rounded-full bg-mint" style={{ animationDelay: '160ms' }} />
              <span className="think-dot w-1.5 h-1.5 rounded-full bg-mint" style={{ animationDelay: '320ms' }} />
            </span>
          ) : (
            <>
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.streaming && (
                <motion.span
                  className="inline-block w-[3px] h-4 bg-mint ml-0.5 align-middle"
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.75, repeat: Infinity }}
                />
              )}
            </>
          )}
        </div>

        {message.citations && message.citations.length > 0 && (() => {
          const groupedMap = new Map<string, any>();
          
          message.citations.forEach(cit => {
            const key = (cit.doc_id && cit.doc_id !== 'unknown') ? cit.doc_id : cit.filename;
            if (!groupedMap.has(key)) {
              groupedMap.set(key, { 
                ...cit, 
                page_numbers: [...(cit.page_numbers || [])],
                chunk_index: undefined // Hide specific chunk when aggregating at document level
              });
            } else {
              const existing = groupedMap.get(key);
              if (cit.page_numbers) {
                existing.page_numbers = Array.from(new Set([...existing.page_numbers, ...cit.page_numbers])).sort((a, b) => a - b);
              }
            }
          });
          
          const uniqueCitations = Array.from(groupedMap.values());

          return (
            <div className={cn('flex flex-wrap gap-1.5', isUser && 'justify-end')}>
              {uniqueCitations.map((cit, i) => (
                <CitationChip key={`${cit.doc_id || cit.filename}-${i}`} citation={cit} />
              ))}
            </div>
          );
        })()}

        {message.agent_trigger && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
            <Link href={`/agents/diagnose/${message.agent_trigger.job_id}`}>
              <Badge variant="warning" className="cursor-pointer hover:bg-signal/20 transition-colors">
                <ArrowUpRight className="w-3 h-3" />
                escalated · {message.agent_trigger.worker}
              </Badge>
            </Link>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
