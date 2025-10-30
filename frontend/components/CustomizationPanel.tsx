import React, { useState, useRef } from 'react';
import { Upload, Zap, Check, AlertCircle, Loader } from 'lucide-react';

interface ThemeOption {
  id: string;
  name: string;
  type: 'light' | 'dark' | 'custom';
  colors: Record<string, string>;
  preview?: string;
}

interface GeneratedImage {
  id: string;
  url: string;
  prompt: string;
  source: 'runway' | 'q-assistant';
  appliedAt?: string;
}

interface CustomizationPanelProps {
  onThemeApply?: (theme: ThemeOption) => void;
  onImageApply?: (image: GeneratedImage) => void;
  currentTheme?: ThemeOption;
}

export const CustomizationPanel: React.FC<CustomizationPanelProps> = ({
  onThemeApply,
  onImageApply,
  currentTheme,
}) => {
  const [activeTab, setActiveTab] = useState<'ai-generated' | 'upload' | 'preview'>('ai-generated');
  const [generationPrompt, setGenerationPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedImages, setUploadedImages] = useState<GeneratedImage[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [theme, setTheme] = useState<ThemeOption>(
    currentTheme || {
      id: 'default-dark',
      name: 'Default Dark',
      type: 'dark',
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        background: '#1f2937',
        text: '#f3f4f6',
        accent: '#ec4899',
      },
    }
  );
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // ===== AI Generation Section =====

  const handleGenerateImage = async () => {
    if (!generationPrompt.trim()) {
      setMessage({ type: 'error', text: 'Please enter a prompt' });
      return;
    }

    setIsGenerating(true);
    setMessage(null);

    try {
      // Call Q-Assistant API to generate theme/image
      const response = await fetch('/api/v1/customization/generate-theme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: generationPrompt,
          imageSize: '512x512',
        }),
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      const data = await response.json();

      const newImage: GeneratedImage = {
        id: data.id || `gen_${Date.now()}`,
        url: data.imageUrl || data.url,
        prompt: generationPrompt,
        source: data.source || 'q-assistant',
      };

      setGeneratedImages([newImage, ...generatedImages]);
      setSelectedImageId(newImage.id);
      setGenerationPrompt('');
      setMessage({
        type: 'success',
        text: 'Theme generated successfully!',
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApplyGeneratedImage = async () => {
    if (!selectedImageId) return;

    const image = generatedImages.find((img) => img.id === selectedImageId);
    if (!image) return;

    try {
      // Apply theme/image
      onImageApply?.(image);

      const updatedImage = { ...image, appliedAt: new Date().toISOString() };
      setGeneratedImages(generatedImages.map((img) => (img.id === selectedImageId ? updatedImage : img)));

      setMessage({
        type: 'success',
        text: 'Theme applied successfully!',
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to apply theme',
      });
    }
  };

  // ===== File Upload Section =====

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      const reader = new FileReader();

      reader.onload = async (event) => {
        setIsUploading(true);

        try {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('fileName', file.name);

          const response = await fetch('/api/v1/customization/upload-theme', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }

          const data = await response.json();

          const newImage: GeneratedImage = {
            id: `upload_${Date.now()}`,
            url: event.target?.result as string,
            prompt: file.name,
            source: 'q-assistant', // Indicate user upload
          };

          setUploadedImages([newImage, ...uploadedImages]);
          setUploadProgress((prev) => Math.min(prev + 20, 100));

          setMessage({
            type: 'success',
            text: `Uploaded: ${file.name}`,
          });
        } catch (error) {
          setMessage({
            type: 'error',
            text: `Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
          });
        } finally {
          setIsUploading(false);
          setUploadProgress(0);
        }
      };

      reader.readAsDataURL(file);
    });
  };

  const handleApplyUploadedImage = (imageId: string) => {
    const image = uploadedImages.find((img) => img.id === imageId);
    if (!image) return;

    onImageApply?.(image);
    setMessage({
      type: 'success',
      text: 'Theme applied successfully!',
    });
  };

  // ===== Theme Preview Section =====

  const applyTheme = () => {
    onThemeApply?.(theme);
    setMessage({
      type: 'success',
      text: 'Custom theme applied!',
    });
  };

  const updateThemeColor = (colorKey: string, colorValue: string) => {
    setTheme({
      ...theme,
      colors: {
        ...theme.colors,
        [colorKey]: colorValue,
      },
    });
  };

  const predefinedThemes: ThemeOption[] = [
    {
      id: 'dark-blue',
      name: 'Dark Blue',
      type: 'dark',
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        background: '#1f2937',
        text: '#f3f4f6',
        accent: '#ec4899',
      },
    },
    {
      id: 'light-minimal',
      name: 'Light Minimal',
      type: 'light',
      colors: {
        primary: '#2563eb',
        secondary: '#7c3aed',
        background: '#ffffff',
        text: '#1f2937',
        accent: '#db2777',
      },
    },
    {
      id: 'neon-dark',
      name: 'Neon Dark',
      type: 'dark',
      colors: {
        primary: '#00ff00',
        secondary: '#ff00ff',
        background: '#0a0e27',
        text: '#00ff00',
        accent: '#00ffff',
      },
    },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto bg-gray-900 text-gray-50 rounded-lg shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 rounded-t-lg">
        <h2 className="text-2xl font-bold">IDE Customization</h2>
        <p className="text-sm text-gray-100 mt-1">
          Personalize your editor with AI-generated themes or custom uploads
        </p>
      </div>

      {/* Message Alert */}
      {message && (
        <div
          className={`mx-6 mt-4 p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success'
              ? 'bg-green-900/30 border border-green-700'
              : 'bg-red-900/30 border border-red-700'
          }`}
        >
          {message.type === 'success' ? (
            <Check className="w-5 h-5 text-green-400" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-400" />
          )}
          <span className="text-sm">{message.text}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-gray-700 bg-gray-800/50">
        <button
          onClick={() => setActiveTab('ai-generated')}
          className={`flex-1 px-6 py-4 font-semibold transition-colors ${
            activeTab === 'ai-generated'
              ? 'bg-purple-600 text-white'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Zap className="w-4 h-4 inline mr-2" />
          AI Generated
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 px-6 py-4 font-semibold transition-colors ${
            activeTab === 'upload'
              ? 'bg-purple-600 text-white'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Upload className="w-4 h-4 inline mr-2" />
          Upload Custom
        </button>
        <button
          onClick={() => setActiveTab('preview')}
          className={`flex-1 px-6 py-4 font-semibold transition-colors ${
            activeTab === 'preview'
              ? 'bg-purple-600 text-white'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Preview & Apply
        </button>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* AI Generated Tab */}
        {activeTab === 'ai-generated' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold mb-2">
                Describe your ideal theme
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={generationPrompt}
                  onChange={(e) => setGenerationPrompt(e.target.value)}
                  placeholder="e.g., 'Dark theme with blue accents and minimalist design'"
                  className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-50 placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  disabled={isGenerating}
                />
                <button
                  onClick={handleGenerateImage}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg font-semibold transition-colors flex items-center gap-2"
                >
                  {isGenerating ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  {isGenerating ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </div>

            {/* Generated Images Grid */}
            {generatedImages.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold mb-3">Generated Themes</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {generatedImages.map((image) => (
                    <div
                      key={image.id}
                      onClick={() => setSelectedImageId(image.id)}
                      className={`cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                        selectedImageId === image.id
                          ? 'border-purple-500'
                          : 'border-gray-700 hover:border-gray-600'
                      }`}
                    >
                      <img
                        src={image.url}
                        alt={image.prompt}
                        className="w-full h-32 object-cover"
                      />
                      <div className="p-2 bg-gray-800">
                        <p className="text-xs text-gray-300 truncate">{image.prompt}</p>
                        {image.appliedAt && (
                          <div className="flex items-center gap-1 mt-1">
                            <Check className="w-3 h-3 text-green-400" />
                            <span className="text-xs text-green-400">Applied</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {selectedImageId && (
                  <button
                    onClick={handleApplyGeneratedImage}
                    className="mt-4 px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition-colors flex items-center gap-2"
                  >
                    <Check className="w-4 h-4" />
                    Apply Selected Theme
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Upload Custom Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold mb-2">Upload Custom Theme Image</label>
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center cursor-pointer hover:border-purple-500 transition-colors"
              >
                <Upload className="w-12 h-12 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-200 font-semibold">Click to upload or drag & drop</p>
                <p className="text-sm text-gray-400">PNG, JPG, or SVG files (up to 10MB)</p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>

            {isUploading && (
              <div className="w-full bg-gray-800 rounded-lg h-2">
                <div
                  className="bg-purple-600 h-2 rounded-lg transition-all"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}

            {/* Uploaded Images Grid */}
            {uploadedImages.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold mb-3">Your Uploaded Themes</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {uploadedImages.map((image) => (
                    <div
                      key={image.id}
                      className="rounded-lg overflow-hidden border border-gray-700 hover:border-purple-500 transition-all"
                    >
                      <img
                        src={image.url}
                        alt={image.prompt}
                        className="w-full h-32 object-cover"
                      />
                      <div className="p-2 bg-gray-800">
                        <p className="text-xs text-gray-300 truncate">{image.prompt}</p>
                        <button
                          onClick={() => handleApplyUploadedImage(image.id)}
                          className="mt-2 w-full px-2 py-1 bg-purple-600 hover:bg-purple-700 rounded text-xs font-semibold transition-colors"
                        >
                          Apply Theme
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Preview & Apply Tab */}
        {activeTab === 'preview' && (
          <div className="space-y-6">
            {/* Predefined Themes */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Predefined Themes</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {predefinedThemes.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      theme.id === t.id ? 'border-purple-500' : 'border-gray-700'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: t.colors.primary }}
                      ></div>
                      <span className="font-semibold">{t.name}</span>
                    </div>
                    <div className="flex gap-1">
                      {Object.values(t.colors).map((color, idx) => (
                        <div
                          key={idx}
                          className="w-8 h-8 rounded"
                          style={{ backgroundColor: color }}
                        ></div>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Color Picker */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Customize Colors</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(theme.colors).map(([key, color]) => (
                  <div key={key}>
                    <label className="block text-xs font-semibold mb-2 capitalize">{key}</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="color"
                        value={color}
                        onChange={(e) => updateThemeColor(key, e.target.value)}
                        className="w-10 h-10 rounded cursor-pointer"
                      />
                      <input
                        type="text"
                        value={color}
                        onChange={(e) => updateThemeColor(key, e.target.value)}
                        className="flex-1 px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs font-mono"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Live Preview */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Live Preview</h3>
              <div
                className="p-6 rounded-lg space-y-3"
                style={{ backgroundColor: theme.colors.background }}
              >
                <h4
                  className="text-lg font-bold"
                  style={{ color: theme.colors.text }}
                >
                  Sample Heading
                </h4>
                <p
                  className="text-sm"
                  style={{ color: theme.colors.text }}
                >
                  This is sample text to preview your theme colors.
                </p>
                <div className="flex gap-2">
                  <button
                    className="px-3 py-1 rounded text-sm font-semibold"
                    style={{
                      backgroundColor: theme.colors.primary,
                      color: theme.colors.text,
                    }}
                  >
                    Primary
                  </button>
                  <button
                    className="px-3 py-1 rounded text-sm font-semibold"
                    style={{
                      backgroundColor: theme.colors.secondary,
                      color: theme.colors.text,
                    }}
                  >
                    Secondary
                  </button>
                </div>
              </div>
            </div>

            {/* Apply Button */}
            <button
              onClick={applyTheme}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg font-semibold transition-all flex items-center justify-center gap-2"
            >
              <Check className="w-5 h-5" />
              Apply Custom Theme
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomizationPanel;
