/**
 * 人性化文案工具函数
 * 纯函数，无副作用，可单独测试。
 */

export function getTimeGreeting() {
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 11) return '早上好，今天先冲一把？'
  if (hour >= 11 && hour < 18) return '下午了，找个代练上分？'
  if (hour >= 18) return '今晚要上分还是陪玩？'
  return '还没睡？来一把放松一下'
}

const SERVICE_TYPE_LABELS = {
  '代练': '帮你上号代打',
  '陪玩': '组队一起玩',
  '教学': '教学陪玩',
}

const SERVICE_TYPE_CTA = {
  '代练': '找代练上分',
  '陪玩': '找陪玩搭子',
  '教学': '找教学陪玩',
}

const PUBLISH_BUTTON_LABELS = {
  '代练': '发布代练需求',
  '陪玩': '发布陪玩需求',
  '教学': '发布教学需求',
}

export function getServiceTypeLabel(serviceType) {
  return SERVICE_TYPE_LABELS[serviceType] ?? serviceType
}

export function getServiceTypeCTA(serviceType) {
  return SERVICE_TYPE_CTA[serviceType] ?? '立即下单'
}

export function getPublishButtonLabel(serviceType) {
  return PUBLISH_BUTTON_LABELS[serviceType] ?? '发布需求'
}

export function getOrderStatusCopy(status, serviceType) {
  const isBoost = serviceType === '代练'

  const labels = {
    PENDING: isBoost ? '等待代练接单' : '等待陪玩接单',
    LOCKED: isBoost ? '代练上号中' : '陪玩进行中',
    COMPLETED: isBoost ? '代练完成了！' : '这局打完了！',
    DISPUTED: '订单争议中',
    CANCELLED: '订单已取消',
  }

  const subtitles = {
    PENDING: '需求已发出，代练们正在看',
    LOCKED: isBoost ? '代练正在使用你的账号上分' : '陪玩已就位，一起开黑吧',
    COMPLETED: '记得说说这次体验',
    DISPUTED: '平台正在介入处理',
    CANCELLED: '需要重新找吗？',
  }

  return {
    label: labels[status] ?? status,
    subtitle: subtitles[status] ?? '',
  }
}
