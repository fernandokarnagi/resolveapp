export default function LoadingSpinner({ size = 'md' }) {
  const s = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size]
  return (
    <div className="flex justify-center items-center p-8">
      <div className={`${s} border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin`} />
    </div>
  )
}
