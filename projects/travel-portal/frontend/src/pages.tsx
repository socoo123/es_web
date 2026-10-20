import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { attractionRequest, stayRequest, nights } from './contracts';
import type { AttractionRequest } from './contracts';

function CitySelect({ value = '330100' }: { value?: string }) {
  return <label>目的地<select name="cityCode" defaultValue={value}>
    <option value="330100">杭州</option><option value="110100">北京</option>
  </select></label>;
}

function RequestPreview({ value }: { value: unknown }) {
  return <section className="request" aria-label="请求契约">
    <span className="eyebrow">REQUEST CONTRACT</span>
    <h2>准备好的业务请求</h2>
    <pre data-testid="request-json">{JSON.stringify(value, null, 2)}</pre>
    <p>本课验证条件和页面传递。搜索、库存与报价由后续课程接入。</p>
  </section>;
}

export function HomePage() {
  return <>
    <section className="portal-hero">
      <span className="eyebrow">行旅 · 从一段旅程开始</span>
      <h1>下一站，<br />想去哪里？</h1>
      <p>先确定目的地，再寻找景点与住处。今天从第一份清楚的请求开始。</p>
      <span className="stage">F01 · 工程与请求契约</span>
    </section>
    <div className="journeys">
      <Link to="/attractions" className="journey">
        <span className="number">01 / EXPLORE</span><h2>寻找景点 ↗</h2>
        <p>关键词、城市、预算。把“想去西湖”变成明确的搜索条件。</p>
      </Link>
      <Link to="/hotels" className="journey">
        <span className="number">02 / STAY</span><h2>安排住宿 ↗</h2>
        <p>入住与离店、人数与房间。把两晚住宿变成房型报价请求。</p>
      </Link>
    </div>
  </>;
}

export function AttractionsPage() {
  const [request, setRequest] = useState<AttractionRequest | null>(null);
  const [error, setError] = useState('');
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRequest(null);
    try {
      setRequest(attractionRequest(new FormData(event.currentTarget)));
      setError('');
    } catch (cause) { setError((cause as Error).message); }
  }
  return <>
    <span className="eyebrow">01 / 景点旅程</span><h1>把想去的地方写清楚</h1>
    <p>例如：杭州，关键词“西湖”，门票预算不超过 200 元。</p>
    <form onSubmit={submit}>
      <label>关键词<input name="keyword" defaultValue="西湖" maxLength={80} /></label>
      <CitySelect />
      <label>门票预算上限（元）<input name="budgetYuan" type="number" min="0" max="999999.99" step="0.01" defaultValue="200" required /></label>
      <button type="submit">生成景点搜索请求</button>
    </form>
    {error && <p role="alert" className="error">{error}</p>}
    {request && <RequestPreview value={request} />}
  </>;
}

export function HotelsPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [error, setError] = useState('');
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const query = new URLSearchParams();
    for (const [key, value] of form) query.set(key, String(value));
    try {
      stayRequest(query);
      navigate('/rooms?' + query.toString());
    } catch (cause) { setError((cause as Error).message); }
  }
  return <>
    <span className="eyebrow">02 / 酒店旅程</span><h1>先确定这次入住</h1>
    <p>日期使用酒店当地日历日；入住日计费，离店日不计房晚。</p>
    <form onSubmit={submit}>
      <CitySelect value={params.get('cityCode') ?? '330100'} />
      <label>入住日期<input name="checkIn" type="date" defaultValue={params.get('checkIn') ?? '2027-05-01'} required /></label>
      <label>离店日期<input name="checkOut" type="date" defaultValue={params.get('checkOut') ?? '2027-05-03'} required /></label>
      <label>入住人数<input name="guests" type="number" min="1" max="8" step="1" defaultValue={params.get('guests') ?? '2'} required /></label>
      <label>房间数<input name="rooms" type="number" min="1" max="4" step="1" defaultValue={params.get('rooms') ?? '1'} required /></label>
      <button type="submit">查看房型请求</button>
    </form>
    {error && <p role="alert" className="error">{error}</p>}
  </>;
}

export function RoomsPage() {
  const [params] = useSearchParams();
  try {
    const request = stayRequest(params);
    return <>
      <span className="eyebrow">03 / 房型请求</span><h1>{nights(request)} 晚 · {request.guests} 人 · {request.rooms} 间房</h1>
      <p>接下来的服务要找出同一房型、同一价目计划、每晚均有库存的报价。</p>
      <RequestPreview value={request} />
      <Link to={'/hotels?' + params.toString()}>← 修改入住条件</Link>
    </>;
  } catch (cause) {
    return <><h1>入住条件不完整</h1><p role="alert" className="error">{(cause as Error).message}</p>
      <Link to="/hotels">重新选择日期与人数</Link></>;
  }
}
