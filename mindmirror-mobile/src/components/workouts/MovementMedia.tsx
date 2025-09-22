import React from 'react'
import { Platform, Image } from 'react-native'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { WebView } from 'react-native-webview'
import { useVideoPlayer, VideoView } from 'expo-video'
import Markdown from 'react-native-markdown-display'

export type MovementLike = any

export function resolveMovementMedia(m: MovementLike): { imageUrl?: string; videoUrl?: string; description?: string } {
  const imageUrl = m?.imageUrl || m?.gifUrl || m?.movement?.imageUrl || m?.movement?.gifUrl || m?.movement?.movement?.imageUrl || m?.movement?.movement?.gifUrl
  // Prefer shortVideoUrl, then longVideoUrl. Avoid legacy generic videoUrl fields.
  const videoUrl =
    m?.shortVideoUrl ||
    m?.movement?.shortVideoUrl ||
    m?.movement?.movement?.shortVideoUrl ||
    m?.longVideoUrl ||
    m?.movement?.longVideoUrl ||
    m?.movement?.movement?.longVideoUrl
  const description = m?.description || m?.movement?.description || m?.movement?.movement?.description
  return { imageUrl, videoUrl, description }
}

export function MovementThumb({ imageUrl, videoUrl }: { imageUrl?: string | undefined; videoUrl?: string | undefined }) {
  const isImage = typeof imageUrl === 'string' && /\.(png|jpg|jpeg|gif)$/i.test(imageUrl)
  const isMp4 = typeof videoUrl === 'string' && /\.mp4$/i.test(videoUrl || '')

  if (isImage) {
    return (
      <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 160, alignItems: 'center', justifyContent: 'center' }}>
        <Image source={{ uri: imageUrl as string }} style={{ width: '100%', height: '100%', resizeMode: 'cover' }} />
      </Box>
    )
  }

  if (isMp4) {
    const player = useVideoPlayer(videoUrl as string, (p) => { p.loop = false })
    return (
      <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
        <VideoView style={{ width: '100%', height: '100%' }} player={player} allowsFullscreen allowsPictureInPicture />
      </Box>
    )
  }

  if (typeof videoUrl === 'string' && videoUrl.trim()) {
    const url = videoUrl.trim()
    const isYouTube = /(?:youtube\.com\/watch\?v=|youtu\.be\/)/i.test(url)
    const isVimeo = /(?:vimeo\.com\/|player\.vimeo\.com\/video\/)/i.test(url)
    let embedUrl = url
    if (isYouTube) {
      try {
        const u = new URL(url)
        const vid = u.hostname.includes('youtu.be') ? u.pathname.replace('/', '') : (u.searchParams.get('v') || '')
        if (vid) embedUrl = `https://www.youtube.com/embed/${vid}`
      } catch {}
    } else if (isVimeo) {
      try {
        if (!/player\.vimeo\.com\/video\//i.test(url)) {
          const m = url.match(/vimeo\.com\/(\d+)/i)
          if (m && m[1]) embedUrl = `https://player.vimeo.com/video/${m[1]}`
        }
      } catch {}
    }
    if (Platform.OS === 'web') {
      return (
        <Box pointerEvents="none" className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
          {/* eslint-disable-next-line react/no-unknown-property */}
          <iframe src={embedUrl} style={{ width: '100%', height: '100%', border: '0' }} allow="autoplay; fullscreen; picture-in-picture" />
        </Box>
      )
    }
    return (
      <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
        <WebView source={{ uri: embedUrl }} allowsInlineMediaPlayback javaScriptEnabled />
      </Box>
    )
  }

  return (
    <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-100" style={{ height: 120, alignItems: 'center', justifyContent: 'center' }}>
      <Text className="text-typography-500">No preview</Text>
    </Box>
  )
}

export function MovementDescription({ description }: { description?: string }) {
  if (!description) return null
  return (
    <Box className="p-2 rounded border border-border-200 bg-background-50 dark:bg-background-100">
      <Markdown>{description}</Markdown>
    </Box>
  )
}


