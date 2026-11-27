/**
 * 素材管理API
 */
import request from '@/utils/request'

/**
 * 上传素材
 */
export const uploadMedia = (formData, onProgress) => {
  return request({
    url: '/media/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onProgress
  })
}

/**
 * 获取素材列表
 */
export const getMediaList = (params) => {
  return request({
    url: '/media/',
    method: 'get',
    params
  })
}

/**
 * 获取素材详情
 */
export const getMediaDetail = (mediaId) => {
  return request({
    url: `/media/${mediaId}`,
    method: 'get'
  })
}

/**
 * 删除素材
 */
export const deleteMedia = (mediaId) => {
  return request({
    url: `/media/${mediaId}`,
    method: 'delete'
  })
}

/**
 * 获取素材下载URL
 */
export const getMediaDownloadUrl = (mediaId) => {
  return `/api/v1/media/${mediaId}/download`
}

/**
 * 获取缩略图URL
 */
export const getThumbnailUrl = (mediaId) => {
  return `/api/v1/media/${mediaId}/thumbnail`
}
