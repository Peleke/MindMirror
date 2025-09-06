'use client';
import React, { useEffect, useLayoutEffect } from 'react';
import { config } from './config';
import { OverlayProvider } from '@gluestack-ui/overlay';
import { ToastProvider } from '@gluestack-ui/toast';
import { setFlushStyles } from '@gluestack-ui/nativewind-utils/flush';
import { script } from './script';

export type ModeType = 'light' | 'dark' | 'system';
export type ThemeVariantId = keyof typeof config['variants'] | undefined;

const variableStyleTagId = 'nativewind-style';
const createStyle = (styleTagId: string) => {
  const style = document.createElement('style');
  style.id = styleTagId;
  style.appendChild(document.createTextNode(''));
  return style;
};

export const useSafeLayoutEffect =
  typeof window !== 'undefined' ? useLayoutEffect : useEffect;

export function GluestackUIProvider({
  mode = 'light',
  themeId,
  ...props
}: {
  mode?: ModeType;
  themeId?: ThemeVariantId;
  children?: React.ReactNode;
}) {
  let cssVariablesWithMode = ``;
  (['light', 'dark'] as const).forEach((configKey) => {
    cssVariablesWithMode +=
      configKey === 'dark' ? `\n .dark {\n ` : `\n:root {\n`;
    const scheme = config[configKey] as Record<string, string>;
    const cssVariables = Object.keys(scheme).reduce((acc: string, curr: string) => {
      acc += `${curr}:${scheme[curr]}; `;
      return acc;
    }, '');
    cssVariablesWithMode += `${cssVariables} \n}`;
  });

  // Inject variant variables as classes like .theme-brand
  const variants = (config as any).variants as Record<string, Record<string, string>> | undefined;
  if (variants) {
    Object.keys(variants || {}).forEach((key) => {
      const cls = `.theme-${key}`;
      const variantVars = variants[key] || {};
      const cssVariables = Object.keys(variantVars || {}).reduce((acc: string, curr: string) => {
        const val = variantVars[curr as keyof typeof variantVars];
        acc += `${curr}:${val}; `;
        return acc;
      }, '');
      cssVariablesWithMode += `\n${cls} {\n ${cssVariables} \n}`;
    });
  }

  setFlushStyles(cssVariablesWithMode);

  const handleMediaQuery = React.useCallback((e: MediaQueryListEvent) => {
    script(e.matches ? 'dark' : 'light');
  }, []);

  useSafeLayoutEffect(() => {
    if (mode !== 'system') {
      const documentElement = document.documentElement;
      if (documentElement) {
        documentElement.classList.add(mode);
        documentElement.classList.remove(mode === 'light' ? 'dark' : 'light');
        documentElement.style.colorScheme = mode;
        if (themeId) {
          // Remove any prior theme-* classes
          documentElement.className = documentElement.className
            .split(' ')
            .filter((c) => !/^theme-/.test(c))
            .join(' ');
          documentElement.classList.add(`theme-${themeId}`);
        }
      }
    }
  }, [mode, themeId]);

  useSafeLayoutEffect(() => {
    if (mode !== 'system') return;
    const media = window.matchMedia('(prefers-color-scheme: dark)');

    media.addListener(handleMediaQuery);

    return () => media.removeListener(handleMediaQuery);
  }, [handleMediaQuery]);

  useSafeLayoutEffect(() => {
    if (typeof window !== 'undefined') {
      const documentElement = document.documentElement;
      if (documentElement) {
        const head = documentElement.querySelector('head');
        let style = head?.querySelector(`[id='${variableStyleTagId}']`);
        if (!style) {
          style = createStyle(variableStyleTagId);
          style.innerHTML = cssVariablesWithMode;
          if (head) head.appendChild(style);
        }
      }
    }
  }, []);

  return (
    <>
      <script
        suppressHydrationWarning
        dangerouslySetInnerHTML={{
          __html: `(${script.toString()})('${mode}')`,
        }}
      />
      <OverlayProvider>
        <ToastProvider>{props.children}</ToastProvider>
      </OverlayProvider>
    </>
  );
}
