"use client";

import { useState } from "react";
import PdfUploader from "@/components/PdfUploader";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            PDF Translator
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Translate your PDFs between Hindi and English while preserving formatting
          </p>
        </div>

        <PdfUploader />

        <div className="mt-16 text-center">
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-6">
            How it works
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">📄</div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                1. Upload PDF
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Upload your PDF file in Hindi or English
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">🔄</div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                2. Select Languages
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Choose source and target languages
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
              <div className="text-4xl mb-4">⬇️</div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                3. Download
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Get your translated PDF with preserved format
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="text-center py-8 text-gray-600 dark:text-gray-400">
        <p>Built with Next.js and FastAPI</p>
      </footer>
    </div>
  );
}
