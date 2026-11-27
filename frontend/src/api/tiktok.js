/**
 * TikTok相关API
 */
import request from '@/utils/request'

/**
 * 发起TikTok授权
 */
export const initiateTikTokAuth = () => {
  return request({
    url: '/tiktok/auth',
    method: 'get'
  })
}

/**
 * 获取TikTok账号列表
 */
export const getTikTokAccounts = () => {
  return request({
    url: '/tiktok/accounts',
    method: 'get'
  })
}

/**
 * 获取TikTok账号详情
 */
export const getTikTokAccount = (accountId) => {
  return request({
    url: `/tiktok/accounts/${accountId}`,
    method: 'get'
  })
}

/**
 * 删除TikTok账号
 */
export const deleteTikTokAccount = (accountId) => {
  return request({
    url: `/tiktok/accounts/${accountId}`,
    method: 'delete'
  })
}

/**
 * 刷新TikTok令牌
 */
export const refreshTikTokToken = (accountId) => {
  return request({
    url: `/tiktok/accounts/${accountId}/refresh`,
    method: 'post'
  })
}
