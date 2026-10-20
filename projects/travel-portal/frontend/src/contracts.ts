// F01 business contracts. Search/quote services are implemented in later lessons.
export type AttractionRequest = {
  keyword: string;
  cityCode: string;
  maxPriceCent: number;
  sort: 'relevance';
  page: number;
  pageSize: number;
};

export type StayRequest = {
  cityCode: string;
  checkIn: string;
  checkOut: string;
  guests: number;
  rooms: number;
};

export function attractionRequest(form: FormData): AttractionRequest {
  const budget = String(form.get('budgetYuan') ?? '');
  if (!/^\d{1,6}(\.\d{1,2})?$/.test(budget)) {
    throw new Error('预算需要是 0–999999.99 元，最多两位小数');
  }
  const [yuan, fraction = ''] = budget.split('.');
  const cityCode = String(form.get('cityCode') ?? '');
  if (!['330100', '110100'].includes(cityCode)) throw new Error('请选择支持的城市');
  return {
    keyword: String(form.get('keyword') ?? '').trim(),
    cityCode,
    maxPriceCent: Number(yuan) * 100 + Number(fraction.padEnd(2, '0')),
    sort: 'relevance', page: 1, pageSize: 10,
  };
}

function validDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(value + 'T00:00:00Z');
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
}

export function stayRequest(params: URLSearchParams): StayRequest {
  const cityCode = params.get('cityCode') ?? '';
  const checkIn = params.get('checkIn') ?? '';
  const checkOut = params.get('checkOut') ?? '';
  const guestText = params.get('guests') ?? '';
  const roomText = params.get('rooms') ?? '';
  if (!['330100', '110100'].includes(cityCode)) throw new Error('请选择支持的城市');
  if (!validDate(checkIn) || !validDate(checkOut) || checkOut <= checkIn) {
    throw new Error('离店日必须晚于入住日，日期需要真实有效');
  }
  if (!/^[1-8]$/.test(guestText) || !/^[1-4]$/.test(roomText)) {
    throw new Error('入住人数为 1–8 人，房间数为 1–4 间');
  }
  return { cityCode, checkIn, checkOut, guests: Number(guestText), rooms: Number(roomText) };
}

export function nights(request: StayRequest): number {
  return (Date.parse(request.checkOut + 'T00:00:00Z') - Date.parse(request.checkIn + 'T00:00:00Z')) / 86400000;
}
