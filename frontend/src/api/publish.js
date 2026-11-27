/**
 * 发布管理API
 */
import request from '@/utils/request'

/**
 * 发布视频
 */
export const publishVideo = (data) => {
  return request({
    url: '/publish/video',
    method: 'post',
    data
  })
}

/**
 * 获取发布记录列表
 */
export const getPublishRecords = (params) => {
  return request({
    url: '/publish/records',
    method: 'get',
    params
  })
}

/**
 * 获取发布记录详情
 */
export const getPublishRecordDetail = (recordId) => {
  return request({
    url: `/publish/records/${recordId}`,
    method: 'get'
  })
}

/**
 * 检查发布状态
 */
export const checkPublishStatus = (recordId) => {
  return request({
    url: `/publish/records/${recordId}/check-status`,
    method: 'post'
  })
}
