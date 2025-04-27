import { Upload } from "./components/upload"
import { Logo } from "./components/logo"

export default function Home() {
  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Video Background */}
      <div className="absolute inset-0 z-0">
        <video
          autoPlay
          muted
          loop
          playsInline
          className="w-full h-full object-cover"
          poster="/cerulean-flow.png"
        >
          <source src="/videos/background.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        {/* Overlay to ensure text readability */}
        <div className="absolute inset-0 bg-blue-900/30 backdrop-blur-sm"></div>
      </div>

      {/* Content */}
      <div className="container max-w-4xl mx-auto px-4 py-8 relative z-10">
        <div className="flex flex-col items-center justify-center space-y-8 pt-12">
          <Logo />

          <div className="text-center space-y-4 max-w-2xl">
            <h1 className="text-3xl md:text-4xl font-bold text-white">
              Form better connections, one conversation at a time
            </h1>
            <p className="text-gray-100 text-lg">
              Upload your conversation and get personalized insights to help you communicate more effectively.
            </p>
          </div>

          <div className="w-full max-w-md mt-8">
            <Upload />
          </div>

          <div className="mt-12 text-center text-sm text-gray-200 max-w-md">
            <p>Your conversations are analyzed securely and privately. We never share your data with third parties.</p>
          </div>
        </div>
      </div>
    </main>
  )
}
