// Nilai extra bersifat publik dan dibundel ke aplikasi. Jangan simpan rahasia.
module.exports = ({ config }) => {
  const value = (process.env.EXPO_PUBLIC_API_URL || '').trim();
  let apiBaseUrl = null;

  if (value) {
    let url;
    try {
      url = new URL(value);
    } catch {
      throw new Error('EXPO_PUBLIC_API_URL harus berupa URL HTTP(S) yang valid.');
    }
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
      throw new Error('EXPO_PUBLIC_API_URL harus HTTP(S), tanpa kredensial, query, atau fragment.');
    }
    apiBaseUrl = url.toString().replace(/\/+$/, '');
  }

  return {
    ...config,
    extra: { ...config.extra, apiBaseUrl },
  };
};
