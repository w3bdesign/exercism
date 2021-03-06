const SECONDS = 31557600;
const planets = {
  earth: 1,
  mercury: 0.2408467,
  venus: 0.61519726,
  mars: 1.8808158,
  jupiter: 11.862615,
  saturn: 29.447498,
  uranus: 84.016846,
  neptune: 164.79132
};
export const age = (planetname, planetseconds) => {
  let temporary = ((planetseconds / SECONDS / planets[planetname]) * 100) / 100;
  return Number(temporary.toFixed(2));
};
