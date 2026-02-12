import ChatWidget from './components/ChatWidget';

function App() {
  return (
    // 'relative z-50' ensures it stays on top.
    // We do NOT add any background colors here.
    <div className="w-full h-full bg-transparent">
      <ChatWidget />
    </div>
  );
}

export default App;