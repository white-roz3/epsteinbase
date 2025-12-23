import React, { useState, useEffect } from 'react';
import { 
  Search, Video, Music, Image, Mail, FileText, Download, ExternalLink, 
  Play, Clock, Calendar, MapPin, User, Info, Filter, Grid, List,
  ChevronRight, AlertCircle, Database, Eye, Lock, Unlock, X, Plane
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Embedded sample data - shows immediately, replaced by API when available
const SAMPLE_DATA = {
  videos: [
    {
      id: 'v1',
      title: 'MCC Cell Block Surveillance - Raw Footage',
      source: 'DOJ',
      type: 'video',
      date: 'August 9-10, 2019',
      duration: '12+ hours',
      url: 'https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video1.mp4',
      location: 'Metropolitan Correctional Center, New York',
      description: 'Unedited surveillance footage from the Special Housing Unit (SHU) tier where Jeffrey Epstein was held.',
      context: 'July 2025 FBI memo concluded no one entered Epstein\'s cell. Guards later charged with falsifying records.',
      thumbnail: null
    },
    {
      id: 'v2',
      title: 'MCC Surveillance - Enhanced Version',
      source: 'DOJ',
      type: 'video',
      date: 'August 9-10, 2019',
      duration: '12+ hours',
      url: 'https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/video2.mp4',
      location: 'Metropolitan Correctional Center, New York',
      description: 'Digitally enhanced version with improved visibility for the low-light corridor footage.',
      context: 'DOJ released both raw and enhanced versions to address claims the original was too dark.',
      thumbnail: null
    },
  ],
  audio: [
    {
      id: 'a1',
      title: 'Maxwell Proffer - Day 1, Part 1',
      source: 'DOJ',
      type: 'audio',
      date: 'July 24, 2025',
      url: 'https://www.justice.gov/multimedia/DOJ%20Disclosures/Maxwell%20Proffer/Audio/Day%201%20-%20Part%201%20-%207_24_25_Tallahassee.003.wav',
      location: 'FCI Tallahassee',
      description: 'First segment of Ghislaine Maxwell\'s proffer session with DOJ prosecutors.',
      context: 'Maxwell cooperating following her 2022 conviction. She is serving a 20-year sentence.',
      redacted: false
    },
    {
      id: 'a2',
      title: 'Maxwell Proffer - Day 1, Part 2',
      source: 'DOJ',
      type: 'audio',
      date: 'July 24, 2025',
      redacted: false
    },
    {
      id: 'a3',
      title: 'Maxwell Proffer - Day 1, Part 3',
      source: 'DOJ',
      type: 'audio',
      date: 'July 24, 2025',
      redacted: true
    },
    {
      id: 'a4',
      title: 'Maxwell Proffer - Day 2, Part 1',
      source: 'DOJ',
      type: 'audio',
      date: 'July 25, 2025',
      redacted: true
    },
  ],
  images: [
    {
      id: 'i1',
      title: 'Clinton in Hot Tub',
      source: 'DOJ',
      type: 'image',
      date: 'Released Dec 19, 2025',
      description: 'Former President Bill Clinton in a hot tub. Another person present but face redacted by DOJ.',
      people: ['Bill Clinton', '[Redacted]'],
      context: 'Clinton acknowledged flying on Epstein\'s plane but denied knowledge of criminal activity.'
    },
    {
      id: 'i2',
      title: 'Clinton and Epstein Standing Together',
      source: 'DOJ',
      type: 'image',
      date: 'Released Dec 19, 2025',
      people: ['Bill Clinton', 'Jeffrey Epstein']
    },
    {
      id: 'i3',
      title: 'Epstein with Michael Jackson',
      source: 'DOJ',
      type: 'image',
      date: 'Released Dec 19, 2025',
      description: 'Epstein standing with Michael Jackson in front of artwork.',
      people: ['Jeffrey Epstein', 'Michael Jackson']
    },
    {
      id: 'i4',
      title: 'Clinton with Kevin Spacey - Churchill War Rooms',
      source: 'DOJ',
      type: 'image',
      date: 'October 2002',
      description: 'Clinton in London with Kevin Spacey inside the Cabinet Room of the Churchill War Rooms.',
      people: ['Bill Clinton', 'Kevin Spacey', 'Doug Band'],
      context: 'From Clinton\'s 2002 Africa trip aboard Epstein\'s jet with Spacey and Chris Tucker.'
    },
    {
      id: 'i5',
      title: 'Epstein with Walter Cronkite',
      source: 'DOJ',
      type: 'image',
      date: '2007',
      people: ['Jeffrey Epstein', 'Walter Cronkite'],
      context: 'Cronkite was "the most trusted man in America." Shows Epstein\'s media access.'
    },
    {
      id: 'i6',
      title: 'Framed Trump Check',
      source: 'DOJ',
      type: 'image',
      date: 'Released Dec 19, 2025',
      description: 'Framed check from Trump to Epstein with caption "once in a blue moon."',
      people: ['Donald Trump', 'Jeffrey Epstein'],
      context: 'Found among estate photos. Trump has denied inappropriate relationship with Epstein.'
    },
  ],
  documents: [
    {
      id: 'd1',
      title: 'Flight Logs (Lolita Express)',
      source: 'DOJ',
      type: 'document',
      subtype: 'Evidence',
      format: 'PDF',
      url: 'https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/B.%20Flight%20Log%20Released%20in%20US%20v.%20Maxwell,%201.20-cr-00330%20(SDNY%202020).pdf',
      description: 'Flight logs from Epstein\'s Boeing 727 showing passengers and destinations.',
    },
    {
      id: 'd2',
      title: 'Contact Book (Black Book)',
      source: 'DOJ',
      type: 'document',
      subtype: 'Evidence',
      format: 'PDF - Redacted',
      url: 'https://www.justice.gov/multimedia/DOJ%20Disclosures/First%20Phase%20of%20Declassified%20Epstein%20Files/C.%20Contact%20Book%20(Redacted).pdf',
      description: 'Personal contact book. Unredacted version reportedly has 1,500+ names.',
    },
    {
      id: 'd3',
      title: 'DOJ/FBI Memo on BOP Footage',
      source: 'DOJ',
      type: 'document',
      subtype: 'Memo',
      format: 'PDF',
      date: 'July 2025',
      url: 'https://www.justice.gov/multimedia/DOJ%20Disclosures/BOP%20Video%20Footage/2025.07%20DOJ%20FBI%20Memorandum.pdf',
      description: 'Concludes no evidence Epstein was murdered or kept a "client list."',
    },
    {
      id: 'd4',
      title: 'EPSTEIN_FILES_20K Dataset',
      source: 'HuggingFace',
      type: 'document',
      subtype: 'Dataset',
      format: 'CSV (106MB)',
      url: 'https://huggingface.co/datasets/tensonaut/EPSTEIN_FILES_20K',
      description: '25,000+ OCR\'d documents in single CSV for analysis and search.',
      count: '25,000+'
    },
    {
      id: 'd5',
      title: 'Combined All Files (Searchable)',
      source: 'Internet Archive',
      type: 'document',
      subtype: 'Archive',
      format: 'PDF (6GB)',
      url: 'https://archive.org/details/combined-all-epstein-files',
      description: 'All DOJ DataSets 1-7 combined into searchable PDFs by researchers.',
      count: '4,055+ documents'
    },
  ],
  emails: [
    {
      id: 'e1',
      title: 'Epstein Estate Email Archive',
      source: 'House Oversight',
      type: 'email',
      date: 'November 2025',
      url: 'https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/',
      description: '20,000+ pages of emails from estate.',
      highlights: ['Trump mentioned 1000+ times', 'Correspondence with Larry Summers', 'Attempts to reconnect with Bill Gates'],
      count: '20,000+ pages'
    },
    {
      id: 'e2',
      title: 'Structured Email Dataset',
      source: 'HuggingFace',
      type: 'email',
      url: 'https://huggingface.co/datasets/to-be/epstein-emails',
      description: 'Vision LLM-processed emails with SQLite database.',
      webapp: 'https://epsteinsphone.org',
      format: 'SQLite + Web App'
    },
  ]
};

const SOURCE_COLORS = {
  'DOJ': 'bg-blue-500/10 text-blue-700 border-blue-500/20',
  'House Oversight': 'bg-purple-500/10 text-purple-700 border-purple-500/20',
  'HuggingFace': 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20',
  'Internet Archive': 'bg-orange-500/10 text-orange-700 border-orange-500/20',
};

const TABS = [
  { id: 'all', label: 'All Files', icon: Database },
  { id: 'videos', label: 'Videos', icon: Video },
  { id: 'audio', label: 'Audio', icon: Music },
  { id: 'images', label: 'Images', icon: Image },
  { id: 'flightlogs', label: 'Flight Logs', icon: Plane },
  { id: 'emails', label: 'Emails', icon: Mail },
  { id: 'documents', label: 'Documents', icon: FileText },
];

// Stats banner component
function StatsBanner({ stats, useApi }) {
  const items = [
    { label: 'DOJ Documents', value: stats.doj ? stats.doj.toLocaleString() : '0', icon: FileText },
    { label: 'Videos', value: stats.videos ? stats.videos.toLocaleString() : '0', icon: Video },
    { label: 'Audio Files', value: stats.audio ? stats.audio.toLocaleString() : '0', icon: Music },
    { label: 'Photos', value: stats.images ? stats.images.toLocaleString() : '0', icon: Image },
  ];

  return (
    <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4 mb-4">
          <div className="flex-1">
            <h1 className="text-xl sm:text-2xl font-bold">Epstein Files Database</h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-1">
              December 2025 DOJ Release • Searchable Archive
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
          {items.map((item, i) => (
            <div key={i} className="bg-white/5 rounded-lg p-2.5 sm:p-3 border border-white/10">
              <div className="flex items-center gap-1.5 sm:gap-2 text-slate-400 text-xs mb-1">
                <item.icon className="w-3 h-3 sm:w-3.5 sm:h-3.5 flex-shrink-0" />
                <span className="truncate">{item.label}</span>
              </div>
              <div className="text-lg sm:text-xl font-semibold truncate">{item.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Source badge
function SourceBadge({ source }) {
  const colors = SOURCE_COLORS[source] || 'bg-gray-100 text-gray-700 border-gray-200';
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded border ${colors}`}>
      {source}
    </span>
  );
}

// Video card
function VideoCard({ item }) {
  const videoUrl = item.url || item.file_path;
  if (!videoUrl) return null;
  
  return (
    <a 
      href={videoUrl} 
      target="_blank" 
      rel="noopener noreferrer"
      className="group bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-xl hover:border-gray-300 transition-all"
    >
      <div className="aspect-video bg-gradient-to-br from-gray-900 to-gray-800 relative">
        <div className="absolute inset-0 flex items-center justify-center">
          <Video className="w-12 h-12 text-gray-600" />
        </div>
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center transform group-hover:scale-110 transition-transform">
            <Play className="w-7 h-7 text-gray-900 ml-1" />
          </div>
        </div>
        {item.duration && (
          <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded font-mono">
            {item.duration}
          </div>
        )}
        <div className="absolute top-2 left-2">
          <SourceBadge source={item.source} />
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
          {item.title}
        </h3>
        <p className="text-sm text-gray-600 line-clamp-2 mb-3">{item.description}</p>
        {item.context && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-2 mb-3">
            <p className="text-xs text-amber-800 line-clamp-2">{item.context}</p>
          </div>
        )}
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {item.location && (
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              <span className="truncate max-w-[150px]">{item.location}</span>
            </span>
          )}
          {item.date && (
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {item.date}
            </span>
          )}
        </div>
      </div>
    </a>
  );
}

// Audio card
function AudioCard({ item }) {
  // Construct audio URL - prioritize external URL, then file_path
  let audioUrl = null;
  if (item.url) {
    audioUrl = item.url;
  } else if (item.file_path) {
    audioUrl = `${API_BASE}/files/${item.file_path}`;
  }
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-gray-300 transition-all">
      <div className="flex gap-4">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-violet-500/20">
          <Music className="w-7 h-7 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-gray-900 truncate">{item.title}</h3>
            {item.redacted && (
              <span className="flex items-center gap-1 text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                <Lock className="w-3 h-3" />
                Redacted
              </span>
            )}
            {item.redacted === false && (
              <span className="flex items-center gap-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                <Unlock className="w-3 h-3" />
                Full
              </span>
            )}
          </div>
          {item.description && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-1">{item.description}</p>
          )}
          {item.context && (
            <p className="text-xs text-gray-500 bg-gray-50 rounded p-2 mb-2 line-clamp-2">{item.context}</p>
          )}
          
          {/* Audio Player */}
          {audioUrl ? (
            <div className="mb-3">
              <audio
                key={audioUrl} // Force re-render if URL changes
                src={audioUrl}
                preload="metadata"
                className="w-full h-9"
                controls
                style={{
                  outline: 'none'
                }}
                onError={(e) => {
                  console.error('Audio failed to load:', audioUrl, e.target.error);
                }}
                onCanPlay={(e) => {
                  console.log('Audio can play:', audioUrl);
                }}
                onLoadedMetadata={(e) => {
                  console.log('Audio metadata loaded:', audioUrl, 'Duration:', e.target.duration);
                }}
              >
                Your browser does not support the audio element.
              </audio>
            </div>
          ) : (
            <div className="mb-3 text-xs text-gray-500">Audio URL not available</div>
          )}
          
          <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
            <SourceBadge source={item.source} />
            {item.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {item.location}
              </span>
            )}
            {item.date && (
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {item.date}
              </span>
            )}
            {audioUrl && (
              <a 
                href={audioUrl} 
                download
                className="flex items-center gap-1 text-blue-600 hover:text-blue-700"
                onClick={(e) => e.stopPropagation()}
              >
                <Download className="w-3 h-3" />
                Download
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Image card
function ImageCard({ item, onImageClick }) {
  // Prioritize thumbnail_url, then thumbnail, then thumbnail_path, then url, then construct from file_path
  const imageUrl = item.url || (item.file_path && item.file_path.startsWith('http') 
    ? item.file_path 
    : (item.file_path ? `${API_BASE}/files/${item.file_path}` : null));
  
  let thumbUrl = item.thumbnail_url || item.thumbnail || null;
  if (!thumbUrl && item.thumbnail_path) {
    thumbUrl = item.thumbnail_path.startsWith('http') || item.thumbnail_path.startsWith('/')
      ? item.thumbnail_path
      : `${API_BASE}/files/${item.thumbnail_path}`;
  }
  if (!thumbUrl) {
    thumbUrl = imageUrl;
  }
  
  // Don't render if we have no valid URLs at all
  if (!imageUrl && !thumbUrl) {
    return null;
  }
  
  return (
    <div
      onClick={() => onImageClick && imageUrl && onImageClick(item)}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-xl hover:border-gray-300 transition-all group cursor-pointer"
    >
      <div className="aspect-[4/3] bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center relative overflow-hidden">
        {thumbUrl ? (
          <img 
            src={thumbUrl} 
            alt={item.title || 'Image'}
            className="w-full h-full object-cover"
            loading="lazy"
            onError={(e) => {
              console.error('Thumbnail failed to load:', thumbUrl, item.id);
              // Try fallback to main image URL if thumbnail fails
              if (thumbUrl !== imageUrl && imageUrl) {
                e.target.src = imageUrl;
              } else {
                e.target.style.display = 'none';
                if (e.target.nextSibling) {
                  e.target.nextSibling.style.display = 'flex';
                }
              }
            }}
            onLoad={() => {
              console.log('Thumbnail loaded successfully:', item.id);
            }}
          />
        ) : null}
        <div className={`absolute inset-0 flex items-center justify-center ${thumbUrl ? 'hidden' : 'flex'}`}>
          <Image className="w-12 h-12 text-gray-400" />
        </div>
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <Eye className="w-8 h-8 text-white" />
        </div>
        <div className="absolute top-2 left-2">
          <SourceBadge source={item.source} />
        </div>
      </div>
      <div className="p-3 sm:p-4">
        <h3 className="font-semibold text-sm sm:text-base text-gray-900 mb-1.5 sm:mb-2 line-clamp-2">{item.title}</h3>
        {item.description && (
          <p className="text-xs sm:text-sm text-gray-600 mb-2 sm:mb-3 line-clamp-2">{item.description}</p>
        )}
        {item.context && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-2 mb-2 sm:mb-3">
            <p className="text-xs text-amber-800 line-clamp-2">{item.context}</p>
          </div>
        )}
        {item.people && item.people.length > 0 && (
          <div className="mb-2 sm:mb-3">
            <div className="flex flex-wrap gap-1">
              {item.people.slice(0, 3).map((person, i) => (
                <span 
                  key={i} 
                  className="text-xs bg-blue-50 text-blue-700 px-1.5 sm:px-2 py-0.5 rounded-full flex items-center gap-1"
                  title={`Person: ${person}`}
                >
                  <User className="w-2.5 h-2.5 sm:w-3 sm:h-3 flex-shrink-0" />
                  <span className="truncate max-w-[70px] sm:max-w-[100px]">{person}</span>
                </span>
              ))}
            </div>
          </div>
        )}
        {item.metadata && typeof item.metadata === 'object' && (
          <>
            {item.metadata.scene_type && item.metadata.scene_type !== 'unknown' && (
              <div className="mb-2 sm:mb-3">
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded capitalize">
                  {item.metadata.scene_type.replace('_', ' ')}
                </span>
              </div>
            )}
            {item.metadata.objects && item.metadata.objects.length > 0 && (
              <div className="mb-2 sm:mb-3">
                <div className="flex flex-wrap gap-1">
                  {item.metadata.objects.slice(0, 2).map((obj, i) => (
                    <span key={i} className="text-xs bg-gray-100 text-gray-600 px-1.5 sm:px-2 py-0.5 rounded">
                      {obj}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
        {item.date && (
          <div className="text-xs text-gray-500 flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {item.date}
          </div>
        )}
      </div>
    </div>
  );
}

// Document card
function DocumentCard({ item }) {
  return (
    <a 
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-gray-300 transition-all group block"
    >
      <div className="flex gap-3">
        <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-50 transition-colors">
          <FileText className="w-6 h-6 text-gray-500 group-hover:text-blue-600 transition-colors" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
              {item.title}
            </h3>
            {item.format && (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                {item.format}
              </span>
            )}
          </div>
          {item.subtype && (
            <div className="text-xs text-gray-500 mb-1">{item.subtype}</div>
          )}
          <p className="text-sm text-gray-600 line-clamp-2 mb-2">{item.description}</p>
          <div className="flex items-center gap-2">
            <SourceBadge source={item.source} />
            {item.count && (
              <span className="text-xs text-gray-500">{item.count}</span>
            )}
          </div>
        </div>
        <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-blue-600 transition-colors flex-shrink-0" />
      </div>
    </a>
  );
}

// Email card
function EmailCard({ item, onEmailClick }) {
  const metadata = item.metadata || {};
  const from = metadata.from || item.from;
  const to = metadata.to || item.to;
  const subject = metadata.subject || item.subject;
  const emailDate = metadata.date || item.date || item.date_released;
  const bodyPreview = item.context || item.description || (item.ocr_text ? item.ocr_text.substring(0, 200) : '');
  
  return (
    <div 
      onClick={() => onEmailClick && onEmailClick(item)}
      className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-gray-300 transition-all cursor-pointer"
    >
      <div className="flex gap-4">
        <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          <Mail className="w-6 h-6 text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-1">
            {subject || item.title || 'Untitled Email'}
          </h3>
          
          <div className="space-y-1 mb-3 text-sm text-gray-600">
            {from && (
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-700">From:</span>
                <span className="truncate">{from}</span>
              </div>
            )}
            {to && (
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-700">To:</span>
                <span className="truncate">{to}</span>
              </div>
            )}
            {emailDate && (
              <div className="flex items-center gap-2">
                <Calendar className="w-3 h-3" />
                <span>{emailDate}</span>
              </div>
            )}
          </div>
          
          {bodyPreview && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-3">
              {bodyPreview}
            </p>
          )}
          
          <div className="flex items-center gap-3 flex-wrap">
            <SourceBadge source={item.source} />
            {item.efta_id && (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                {item.efta_id}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Email modal for reading full email
function EmailModal({ email, onClose }) {
  if (!email) return null;
  
  const metadata = email.metadata || {};
  const from = metadata.from || email.from;
  const to = metadata.to || email.to;
  const cc = metadata.cc || email.cc;
  const subject = metadata.subject || email.subject || email.title;
  const emailDate = metadata.date || email.date || email.date_released;
  const body = email.ocr_text || email.body || email.context || email.description || '';
  
  return (
    <div 
      className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" 
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 sm:p-6 border-b border-gray-200">
          <div className="flex items-start justify-between mb-3 sm:mb-4">
            <div className="flex items-center gap-2 flex-wrap flex-1 min-w-0">
              <span className={`text-xs sm:text-sm px-2 sm:px-3 py-1 rounded-full ${SOURCE_COLORS[email.source] || 'bg-gray-100 text-gray-600'}`}>
                {email.source?.replace(/_/g, ' ')}
              </span>
              {email.efta_id && (
                <span className="text-xs sm:text-sm bg-gray-100 text-gray-600 px-2 sm:px-3 py-1 rounded-full">
                  {email.efta_id}
                </span>
              )}
            </div>
            <button 
              onClick={onClose} 
              className="text-gray-400 hover:text-gray-600 text-xl sm:text-2xl leading-none p-1 flex-shrink-0 ml-2"
            >
              ×
            </button>
          </div>
          
          <h2 className="text-lg sm:text-2xl font-semibold text-gray-900 mb-3 sm:mb-4 break-words">
            {subject || 'Untitled Email'}
          </h2>
          
          {/* Email metadata */}
          <div className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            {from && (
              <div className="flex flex-col sm:flex-row items-start gap-1 sm:gap-2">
                <span className="font-medium text-gray-700 sm:w-16 flex-shrink-0">From:</span>
                <span className="text-gray-900 flex-1 break-words">{from}</span>
              </div>
            )}
            {to && (
              <div className="flex flex-col sm:flex-row items-start gap-1 sm:gap-2">
                <span className="font-medium text-gray-700 sm:w-16 flex-shrink-0">To:</span>
                <span className="text-gray-900 flex-1 break-words">{to}</span>
              </div>
            )}
            {cc && (
              <div className="flex flex-col sm:flex-row items-start gap-1 sm:gap-2">
                <span className="font-medium text-gray-700 sm:w-16 flex-shrink-0">CC:</span>
                <span className="text-gray-900 flex-1 break-words">{cc}</span>
              </div>
            )}
            {emailDate && (
              <div className="flex flex-col sm:flex-row items-start gap-1 sm:gap-2">
                <span className="font-medium text-gray-700 sm:w-16 flex-shrink-0">Date:</span>
                <span className="text-gray-900 flex-1 break-words">{emailDate}</span>
              </div>
            )}
          </div>
        </div>
        
        {/* Email body */}
        <div className="p-4 sm:p-6 overflow-auto flex-1">
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed">
              {body}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

// Section header
function SectionHeader({ icon: Icon, title, count, onViewAll }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5 text-gray-700" />
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        {count !== undefined && (
          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
            {count}
          </span>
        )}
      </div>
      {onViewAll && (
        <button 
          onClick={onViewAll}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
        >
          View all
          <ChevronRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

// Main App
export default function App() {
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [apiData, setApiData] = useState(null);
  const [apiStats, setApiStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useApi, setUseApi] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [people, setPeople] = useState([]);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [showPeopleFilter, setShowPeopleFilter] = useState(false);

  // Try to fetch from API on mount - always use API
  useEffect(() => {
    setUseApi(true); // Always try to use API
    fetch(`${API_BASE}/api/stats`)
      .then(res => {
        if (!res.ok) throw new Error('API not available');
        return res.json();
      })
      .then(data => {
        // Map API response to stats format
        const mappedStats = {
          total: data.total_documents || 0,
          images: data.by_type?.image || data.total_documents || 0,
          videos: data.by_type?.video || 0,
          audio: data.by_type?.audio || 0,
          emails: data.by_type?.email || 0,
          documents: data.by_type?.document || 0,
          doj: data.by_source?.['DOJ'] || 0,
          ...data // Include any other stats from API
        };
        setApiStats(mappedStats);
      })
      .catch((err) => {
        console.error('API stats fetch failed:', err);
        // Set empty stats so loading doesn't hang
        setApiStats({ total_documents: 0, by_type: {}, by_source: {} });
      });
  }, []);

  // Fetch people when on images tab
  useEffect(() => {
    if ((activeTab === 'images' || activeTab === 'flightlogs') && useApi) {
      fetch(`${API_BASE}/api/people?type=image&limit=50`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch people');
          return res.json();
        })
        .then(data => {
          setPeople(Array.isArray(data) ? data : []);
        })
        .catch(err => {
          console.error('Error fetching people:', err);
          setPeople([]);
        });
    } else {
      setPeople([]);
    }
  }, [activeTab, useApi]);

  // Transform API data to match card component expectations
  const transformApiItem = (item) => {
    // Parse metadata if it's a string
    let metadata = {};
    if (typeof item.metadata === 'string') {
      try {
        metadata = JSON.parse(item.metadata);
      } catch (e) {
        metadata = {};
      }
    } else if (item.metadata) {
      metadata = item.metadata;
    }

    // Extract people from metadata (both people array and detected_people)
    const people = metadata.people || [];
    const detected_people = metadata.detected_people || [];
    const all_people = [...new Set([...people, ...detected_people])]; // Combine and dedupe

    // Convert file_path to URL - prioritize API-provided URL (R2 URLs), then curated, then construct from file_path
    let fileUrl = null;
    if (item.url && item.url.startsWith('http')) {
      // Use R2/external URL if provided by API
      fileUrl = item.url;
    } else if (item.url && item.url.startsWith('/curated/')) {
      // Already a curated path
      fileUrl = item.url;
    } else if (item.file_path) {
      // Check if it's a curated path (starts with /curated/)
      if (item.file_path.startsWith('/curated/')) {
        fileUrl = item.file_path;
      } else {
        // Convert file_path to proper URL via /files endpoint (fallback for local files)
        fileUrl = `${API_BASE}/files/${item.file_path}`;
      }
    }

    // Convert thumbnail_path to URL - prioritize API-provided thumbnail_url or thumbnail_path
    let thumbnailUrl = null;
    // First check thumbnail_url field (convenience field from backend)
    if (item.thumbnail_url && (item.thumbnail_url.startsWith('http') || item.thumbnail_url.startsWith('/'))) {
      thumbnailUrl = item.thumbnail_url;
    } else if (item.thumbnail_path && item.thumbnail_path.startsWith('http')) {
      // Use R2/external thumbnail URL if provided by API
      thumbnailUrl = item.thumbnail_path;
    } else if (item.thumbnail_path && item.thumbnail_path.startsWith('/curated/')) {
      // Curated thumbnail path
      thumbnailUrl = item.thumbnail_path;
    } else if (item.thumbnail_path) {
      // Convert thumbnail_path to proper URL via /files endpoint
      thumbnailUrl = `${API_BASE}/files/${item.thumbnail_path}`;
    } else if (item.thumbnail && item.thumbnail.startsWith('http')) {
      // Fallback to thumbnail field if it's a full URL
      thumbnailUrl = item.thumbnail;
    } else if (fileUrl && (item.type === 'image' || item.type === 'photo')) {
      // Fallback to main image URL if no thumbnail available (for images only)
      thumbnailUrl = fileUrl;
    }

    // Generate better title/caption for images
    let title = item.title;
    if ((item.type === 'image' || item.type === 'photo') && title) {
      // Check if description is generic like "Image from R2" or "Image from DOJ"
      const genericDesc = item.description && /^Image from (R2|DOJ|B2)$/i.test(item.description.trim());
      
      // Only replace if it's a filename pattern or has generic description
      const isFilenamePattern = /^(page_\d+|Page \d+|.*\.(png|jpg|jpeg|gif|pdf)$)/i.test(title);
      
      if (isFilenamePattern || genericDesc) {
        // Skip generic descriptions - prioritize other sources
        if (!genericDesc && item.description && item.description.trim() && !/^Image from/i.test(item.description.trim())) {
          title = item.description.trim();
        }
        // Or use context
        else if (item.context && item.context.trim()) {
          title = item.context.trim();
        }
        // Or generate from detected people
        else if (all_people.length > 0) {
          title = all_people.slice(0, 3).join(', ');
          if (all_people.length > 3) title += ` and ${all_people.length - 3} other${all_people.length - 3 > 1 ? 's' : ''}`;
        }
        // Or use scene type from metadata
        else if (metadata.scene_type && metadata.scene_type !== 'unknown') {
          title = metadata.scene_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        // Or use objects if available
        else if (metadata.objects && metadata.objects.length > 0) {
          title = metadata.objects.slice(0, 3).join(', ');
        }
        // Fallback to numbered title
        else {
          title = `Image #${item.id}`;
        }
      }
    }

    return {
      ...item,
      id: item.id.toString(),
      title: title,
      date: item.date || item.date_released,
      people: all_people,
      url: fileUrl, // Use file URL if available
      thumbnail: thumbnailUrl, // Add thumbnail URL
      thumbnail_path: item.thumbnail_path, // Keep original for reference
      metadata: metadata, // Preserve full metadata for display
      // Map API types to frontend types for images
      type: item.type === 'image' ? 'image' : item.type
    };
  };

  // Reset person filter when switching tabs
  useEffect(() => {
    if (activeTab !== 'images' && activeTab !== 'flightlogs') {
      setSelectedPerson(null);
    }
  }, [activeTab]);

  // Load curated files from public folder (Vercel static assets)
  useEffect(() => {
    // Load curated manifest for images/audio
    fetch('/curated/manifest.json')
      .then(res => res.json())
      .then(manifest => {
        console.log('Loaded curated manifest:', manifest);
        
        // Convert curated images to API format
        const curatedImages = (manifest.images || []).map((img, idx) => ({
          id: `curated_img_${idx}`,
          title: img.title,
          type: 'image',
          source: 'DOJ',
          file_path: img.path,
          url: img.path, // Direct path to public folder
          thumbnail: img.path
        }));
        
        // Convert curated audio to API format
        const curatedAudio = (manifest.audio || []).map((audio, idx) => ({
          id: `curated_audio_${idx}`,
          title: audio.title,
          type: 'audio',
          source: 'DOJ',
          file_path: audio.path,
          url: audio.path, // Direct path to public folder
          date: 'July 24-25, 2025',
          description: 'Maxwell proffer session recording'
        }));
        
        setApiData(prev => ({
          ...prev,
          images: [...curatedImages, ...(prev.images || [])],
          audio: [...curatedAudio, ...(prev.audio || [])]
        }));
      })
      .catch(err => {
        console.log('No curated manifest found (using API only):', err);
      });
  }, []);

  // Fetch documents from API when tab changes
  useEffect(() => {
    setLoading(true);
    
    // Use /api/documents endpoint for all tabs (images, videos, audio, etc.)
    const params = new URLSearchParams();
    if (activeTab !== 'all') {
      const typeMap = {
        'videos': 'video',
        'audio': 'audio',
        'images': 'image',
        'emails': 'email',
        'documents': 'document',
        'flightlogs': 'image' // Flight logs are images, filtered by file_path
      };
      params.set('type', typeMap[activeTab] || activeTab);
    }
    
    // Add flightlogs filter: true for flightlogs tab, false for images tab (to exclude flight logs)
    if (activeTab === 'flightlogs') {
      params.set('flightlogs', 'true');
    } else if (activeTab === 'images') {
      params.set('flightlogs', 'false');  // Exclude flight logs from regular images
    }
    
    params.set('page', '1');
    params.set('per_page', '1000');
    const apiUrl = `${API_BASE}/api/documents?${params}`;

    // Add timeout to prevent infinite loading
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
      setApiData(prev => ({
        videos: prev.videos || [],
        audio: prev.audio || [],
        images: prev.images || [],
        documents: [],
        emails: []
      }));
      setLoading(false);
    }, 15000);

    fetch(apiUrl, { signal: controller.signal })
      .then(res => {
        clearTimeout(timeoutId);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
      })
      .then(data => {
        clearTimeout(timeoutId);
        console.log(`[${activeTab}] API response:`, data);
        
        // Group items by type
        const grouped = {
          videos: [],
          audio: [],
          images: [],
          documents: [],
          emails: []
        };
        
        if (data.results && Array.isArray(data.results)) {
          data.results.forEach(item => {
            try {
              const transformed = transformApiItem(item);
              const type = item.type || 'document';
              // Group items by their actual type
              if (type === 'video') grouped.videos.push(transformed);
              else if (type === 'audio') grouped.audio.push(transformed);
              else if (type === 'image') grouped.images.push(transformed);
              else if (type === 'email') grouped.emails.push(transformed);
              else grouped.documents.push(transformed);
            } catch (e) {
              console.error('Error transforming item:', e, item);
            }
          });
        }
        
        // Replace with new data (this ensures videos and images are properly separated)
        setApiData(grouped);
        setLoading(false);
      })
      .catch(err => {
        clearTimeout(timeoutId);
        if (err.name !== 'AbortError') {
          console.error('Error fetching documents:', err);
        }
        setApiData({
          videos: [],
          audio: [],
          images: [],
          documents: [],
          emails: []
        });
        setLoading(false);
      });

    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [activeTab]);

  // Get data based on active tab - ALWAYS use API data only
  const getData = () => {
    // Always return all data regardless of active tab
    const result = {
      videos: apiData?.videos || [],
      audio: apiData?.audio || [],
      images: apiData?.images || [],
      documents: apiData?.documents || [],
      emails: apiData?.emails || []
    };
    return result;
  };

  const data = getData();
  
  // Use API stats only
  const stats = apiStats ? {
    total: apiStats.total_documents || 0,
    videos: apiStats.by_type?.video || 0,
    audio: apiStats.by_type?.audio || 0,
    images: apiStats.by_type?.image || 0,
    documents: apiStats.by_type?.document || 0,
    emails: apiStats.by_type?.email || 0,
    doj: apiStats.by_source?.DOJ || 0,
    flightlogs: apiStats.flightlogs || 0
  } : {
    total: 0,
    videos: 0,
    audio: 0,
    images: 0,
    documents: 0,
    emails: 0,
    doj: 0,
    flightlogs: 0
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4 py-3 sm:py-4">
            {/* Logo */}
            <div className="flex items-center flex-shrink-0 w-full sm:w-auto justify-center sm:justify-start">
              <img 
                src="/epsteinbase-logo.png" 
                alt="EpsteinBase Logo" 
                className="h-12 sm:h-16 w-auto"
              />
            </div>
            
            {/* Search */}
            <div className="w-full sm:w-full sm:max-w-2xl sm:ml-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={activeTab === 'images' ? "Search images or people (e.g., Michael Jackson)..." : "Search..."}
                  className="w-full pl-9 pr-3 py-2 text-sm bg-gray-100 rounded-full border-0 focus:bg-white focus:ring-2 focus:ring-slate-900 transition-all sm:pl-10 sm:pr-4 sm:py-2.5 sm:text-base"
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Banner */}
      <StatsBanner stats={stats} useApi={useApi} />

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-[73px] sm:top-[105px] md:top-16 z-40">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6">
          <nav className="flex gap-0.5 sm:gap-1 -mb-px overflow-x-auto scrollbar-hide pb-px">
            {TABS.map(tab => {
              const Icon = tab.icon;
              // Get count for each tab type
              let count = 0;
              if (tab.id === 'images') {
                count = stats.images || 0;
              } else if (tab.id === 'videos') {
                count = stats.videos || 0;
              } else if (tab.id === 'audio') {
                count = stats.audio || 0;
              } else if (tab.id === 'flightlogs') {
                count = stats.flightlogs || 0;
              } else if (tab.id === 'emails') {
                count = stats.emails || 0;
              } else if (tab.id === 'documents') {
                count = stats.documents || 0;
              } else {
                count = stats.total || 0;
              }
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-1 sm:gap-1.5 md:gap-2 px-2 sm:px-3 md:px-4 py-2 sm:py-2.5 md:py-3 text-xs sm:text-sm font-medium border-b-2 whitespace-nowrap transition-all ${
                    activeTab === tab.id
                      ? 'text-slate-900 border-slate-900'
                      : 'text-gray-500 border-transparent hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
                  <span className="hidden sm:inline">{tab.label}</span>
                  <span className="sm:hidden">{tab.label.split(' ')[0]}</span>
                  <span className={`text-xs px-1 sm:px-1.5 py-0.5 rounded-full transition-colors flex-shrink-0 ${
                    activeTab === tab.id ? 'bg-slate-900 text-white' : 'bg-gray-100 text-gray-500'
                  }`}>
                    {count}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 py-4 sm:py-6 lg:py-8">
        {loading && !data.images?.length && !data.videos?.length && !data.audio?.length && !data.documents?.length && !data.emails?.length && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-slate-900 border-t-transparent rounded-full" />
          </div>
        )}
        
        {/* Images Section - Show first on ALL tab */}
        {data.images && data.images.length > 0 && activeTab !== 'flightlogs' && (
          <section className="mb-12">
            <SectionHeader 
              icon={Image} 
              title="Released Photos" 
              count={activeTab === 'all' ? stats.images : undefined}
              onViewAll={activeTab === 'all' ? () => setActiveTab('images') : undefined}
            />
            {activeTab === 'images' && people.length > 0 && (
              <PeopleFilter
                people={people}
                selectedPerson={selectedPerson}
                onSelectPerson={setSelectedPerson}
                showDropdown={showPeopleFilter}
                setShowDropdown={setShowPeopleFilter}
                totalCount={stats.images || 0}
              />
            )}
            <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
              {data.images
                .filter(item => {
                  // Filter by selected person if set
                  if (selectedPerson) {
                    const itemPeople = (item.people || []).filter(p => p);
                    const metadataPeople = (item.metadata?.detected_people || []).filter(p => p);
                    const allPeople = [...itemPeople, ...metadataPeople].map(p => String(p).toLowerCase());
                    return allPeople.includes(String(selectedPerson.name || '').toLowerCase());
                  }
                  
                  // Filter by search query (searches title, description, and people)
                  if (searchQuery && searchQuery.trim()) {
                    const query = searchQuery.trim().toLowerCase();
                    const itemPeople = (item.people || []).filter(p => p);
                    const metadataPeople = (item.metadata?.detected_people || []).filter(p => p);
                    const allPeople = [...itemPeople, ...metadataPeople].map(p => String(p).toLowerCase());
                    
                    // Search in title, description, context, and people
                    const titleMatch = (item.title || '').toLowerCase().includes(query);
                    const descMatch = (item.description || '').toLowerCase().includes(query);
                    const contextMatch = (item.context || '').toLowerCase().includes(query);
                    const peopleMatch = allPeople.some(p => p.includes(query));
                    
                    return titleMatch || descMatch || contextMatch || peopleMatch;
                  }
                  
                  return true;
                })
                .sort((a, b) => {
                  // Sort images with people to the top
                  const aHasPeople = ((a.people || []).length > 0) || ((a.metadata?.detected_people || []).length > 0);
                  const bHasPeople = ((b.people || []).length > 0) || ((b.metadata?.detected_people || []).length > 0);
                  if (aHasPeople && !bHasPeople) return -1;
                  if (!aHasPeople && bHasPeople) return 1;
                  return 0;
                })
                .map((item, idx) => (
                  <ImageCard 
                    key={item.id || idx} 
                    item={item} 
                    onImageClick={setSelectedImage}
                  />
                ))}
            </div>
          </section>
        )}

        {/* Audio Section - Show after Images on ALL tab */}
        {data.audio && data.audio.length > 0 && (
          <section className="mb-12">
            <SectionHeader 
              icon={Music} 
              title="Maxwell Proffer Recordings" 
              count={activeTab === 'all' ? stats.audio : undefined}
              onViewAll={activeTab === 'all' ? () => setActiveTab('audio') : undefined}
            />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {data.audio.map(item => (
                <AudioCard key={item.id} item={item} />
              ))}
            </div>
          </section>
        )}

        {/* Videos Section */}
        {data.videos && data.videos.length > 0 && (
          <section className="mb-12">
            <SectionHeader 
              icon={Video} 
              title="Surveillance Videos" 
              count={activeTab === 'all' ? stats.videos : undefined}
              onViewAll={activeTab === 'all' ? () => setActiveTab('videos') : undefined}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              {data.videos.map(item => (
                <VideoCard key={item.id} item={item} />
              ))}
            </div>
          </section>
        )}

        {/* Flight Logs Section */}
        {data.images && data.images.length > 0 && activeTab === 'flightlogs' && (
          <section className="mb-12">
            <SectionHeader 
              icon={Plane} 
              title="Flight Logs & Contact Books" 
              count={stats.flightlogs || data.images.length}
            />
            <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
              {data.images.map((item, idx) => (
                <ImageCard 
                  key={item.id || idx} 
                  item={item} 
                  onImageClick={setSelectedImage}
                />
              ))}
            </div>
          </section>
        )}

        {/* Emails Section */}
        {data.emails && data.emails.length > 0 && (
          <section className="mb-12">
            <SectionHeader 
              icon={Mail} 
              title="Email Archives" 
              count={activeTab === 'all' ? stats.emails : undefined}
              onViewAll={activeTab === 'all' ? () => setActiveTab('emails') : undefined}
            />
            <div className="space-y-4">
              {data.emails.map(item => (
                <EmailCard 
                  key={item.id} 
                  item={item}
                  onEmailClick={setSelectedEmail}
                />
              ))}
            </div>
          </section>
        )}

        {/* Documents Section */}
        {data.documents && data.documents.length > 0 && (
          <section className="mb-12">
            <SectionHeader 
              icon={FileText} 
              title="Documents & Datasets" 
              count={activeTab === 'all' ? stats.documents : undefined}
              onViewAll={activeTab === 'all' ? () => setActiveTab('documents') : undefined}
            />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {data.documents.map(item => (
                <DocumentCard key={item.id} item={item} />
              ))}
            </div>
          </section>
        )}

      </main>

      {/* Image Modal/Lightbox */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/95 z-[100] flex items-center justify-center p-2 sm:p-4"
          onClick={() => setSelectedImage(null)}
        >
          <button
            onClick={(e) => { e.stopPropagation(); setSelectedImage(null); }}
            className="absolute top-2 right-2 sm:top-4 sm:right-4 text-white hover:text-gray-300 transition-colors z-10 bg-black/70 hover:bg-black/90 rounded-full p-2 sm:p-2.5"
            aria-label="Close"
          >
            <X className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
          <div 
            className="max-w-7xl w-full h-full flex items-center justify-center"
            onClick={(e) => e.stopPropagation()}
          >
            <img 
              src={selectedImage.url || (selectedImage.file_path && selectedImage.file_path.startsWith('http') 
                ? selectedImage.file_path 
                : (selectedImage.file_path ? `${API_BASE}/files/${selectedImage.file_path}` : null))}
              alt={selectedImage.title || 'Image'}
              className="max-w-full max-h-[90vh] sm:max-h-full object-contain"
              loading="eager"
              crossOrigin="anonymous"
            />
          </div>
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-white text-center bg-black/80 backdrop-blur-sm px-3 py-2 sm:px-4 sm:py-2 rounded-lg max-w-[calc(100%-1rem)] sm:max-w-2xl">
            <h3 className="font-semibold text-sm sm:text-base">{selectedImage.title || 'Untitled Image'}</h3>
            {selectedImage.description && selectedImage.description !== 'Image from R2' && (
              <p className="text-xs sm:text-sm text-gray-300 mt-1 line-clamp-2">{selectedImage.description}</p>
            )}
            {selectedImage.context && (
              <p className="text-xs text-gray-400 mt-1 line-clamp-2">{selectedImage.context}</p>
            )}
            {selectedImage.people && selectedImage.people.length > 0 && (
              <div className="flex flex-wrap gap-1 justify-center mt-1">
                {selectedImage.people.slice(0, 5).map((person, i) => (
                  <span key={i} className="text-xs bg-blue-500/30 text-blue-200 px-2 py-0.5 rounded">
                    {person}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Email Modal */}
      {selectedEmail && (
        <EmailModal email={selectedEmail} onClose={() => setSelectedEmail(null)} />
      )}

      {/* Footer */}
      <footer className="bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 sm:gap-6">
            <div className="text-center md:text-left">
              <div className="flex items-center gap-2 justify-center md:justify-start mb-2">
                <Database className="w-5 h-5" />
                <span className="font-bold">EpsteinBase</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-400 max-w-md">
                Public records aggregator. All documents from official government releases.
              </p>
            </div>
            <div className="flex flex-wrap gap-3 sm:gap-4 md:gap-6 text-xs sm:text-sm justify-center md:justify-end">
              <a 
                href="https://www.justice.gov/epstein" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors whitespace-nowrap"
              >
                DOJ Library
              </a>
              <a 
                href="https://oversight.house.gov" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors whitespace-nowrap"
              >
                House Oversight
              </a>
              <a 
                href="https://archive.org/details/combined-all-epstein-files" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors whitespace-nowrap"
              >
                Internet Archive
              </a>
              <a 
                href="https://huggingface.co/datasets/tensonaut/EPSTEIN_FILES_20K" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-white transition-colors whitespace-nowrap"
              >
                Dataset
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
