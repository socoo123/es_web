import { useState } from 'react';
import { Link, NavLink, Route, Routes } from 'react-router-dom';
import { HealthPanel } from './HealthPanel';
import { HomePage, AttractionsPage, HotelsPage, RoomsPage } from './pages';

export function App() {
  const [dark, setDark] = useState(false);
  return <div className="portal" data-theme={dark ? 'dark' : 'light'}>
    <header className="portal-nav">
      <Link to="/" className="logo">行旅<span>TRAVEL PORTAL</span></Link>
      <nav aria-label="门户导航"><NavLink to="/attractions">景点</NavLink><NavLink to="/hotels">酒店</NavLink></nav>
      <button className="theme" type="button" onClick={() => setDark(!dark)}>{dark ? '浅色' : '深色'}</button>
    </header>
    <main className="portal-main">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/attractions" element={<AttractionsPage />} />
        <Route path="/hotels" element={<HotelsPage />} />
        <Route path="/rooms" element={<RoomsPage />} />
        <Route path="*" element={<><h1>找不到这条旅程</h1><Link to="/">返回首页</Link></>} />
      </Routes>
      <HealthPanel />
    </main>
    <footer className="portal-footer">行旅 / ES 框架学习篇 · 教学项目</footer>
  </div>;
}
